import streamlit as st

from config.settings import BASE_DIR, DEBUG_MODE
from services.ai_service import AIService
from services.analytics_service import AnalyticsService
from services.image_service import ImageStorageService
from services.product_import_service import ProductImportService
from services.product_service import ProductService
from services.store_assistant_service import StoreAssistantService
from services.store_service import StoreService


def render_store_dashboard(
    current_user: dict,
    store_service: StoreService,
    product_service: ProductService,
    analytics_service: AnalyticsService,
    store_assistant_service: StoreAssistantService,
    view: str,
) -> None:
    st.title("Store Dashboard")

    if view == "Product Database":
        _render_products(current_user, store_service, product_service)
    elif view == "Product Analytics":
        _render_analytics(current_user, store_service, analytics_service)
    elif view == "Store Assistant":
        _render_store_assistant(
            current_user,
            store_service,
            store_assistant_service,
        )
    else:
        _render_profile(current_user, store_service)


def _render_profile(current_user: dict, store_service: StoreService) -> None:
    profile = store_service.get_profile(current_user["id"]) or {}
    st.subheader("Store Profile")

    with st.form("store_profile_form"):
        store_name = st.text_input("Store name", value=profile.get("store_name", ""))
        description = st.text_area("Short description", value=profile.get("description", ""))
        website_url = st.text_input("Website link", value=profile.get("website_url", ""))
        address = st.text_input("Physical address", value=profile.get("address", ""))
        gps_map_url = st.text_input(
            "GPS / Map link",
            value=profile.get("gps_map_url", ""),
            placeholder="Paste 2GIS, Yandex Maps, Google Maps, or any map link",
        )

        if st.form_submit_button("Save profile", use_container_width=True):
            try:
                store_service.save_profile(
                    current_user["id"],
                    store_name,
                    description,
                    website_url,
                    address,
                    gps_map_url,
                )
                st.success("Store profile saved.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))


def _render_products(
    current_user: dict,
    store_service: StoreService,
    product_service: ProductService,
) -> None:
    profile = _require_profile(current_user, store_service)
    if profile is None:
        return

    st.subheader("Products")
    store_id = int(profile["id"])

    if DEBUG_MODE:
        with st.expander("Development tools", expanded=False):
            st.caption("Debug-only controls. Hidden unless DEBUG_MODE=true.")
            if st.button("Load demo products", use_container_width=True):
                added_count = product_service.load_demo_products(store_id)
                st.success(f"Added demo products: {added_count}")
                st.rerun()

    with st.form("store_add_product_form", clear_on_submit=True):
        st.markdown("**Add product**")
        product_id = st.text_input("Product ID")
        name = st.text_input("Name")
        barcode = st.text_input("Barcode")
        price = st.number_input("Price", min_value=0.0, step=1000.0)
        description = st.text_area("Short description")
        product_image = st.file_uploader(
            "Product photo",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=False,
        )
        if product_image is not None:
            st.image(product_image, caption="Preview", width=140)

        if st.form_submit_button("Add product", use_container_width=True):
            try:
                product_db_id = product_service.add_product(store_id, product_id, name, barcode, price, description)
                if product_image is not None:
                    image_path = ImageStorageService().save_product_image(product_image, store_id, product_db_id)
                    image_description = AIService().describe_image(image_path)
                    product_service.update_product(
                        store_id,
                        product_id,
                        name,
                        barcode,
                        price,
                        description,
                        image_path=image_path,
                        image_description=image_description,
                    )
                st.success("Product added.")
                st.rerun()
            except Exception as error:
                st.error(str(error))

    _render_product_import(store_id, product_service)

    search_query = st.text_input("Search own products")
    products = (
        product_service.search_products(search_query, store_id)
        if search_query.strip()
        else product_service.list_products(store_id)
    )

    if not products:
        st.caption("No products yet. Add your first product.")
        return

    st.dataframe(
        products,
        hide_index=True,
        use_container_width=True,
        column_config={
            "id": None,
            "store_id": None,
            "image_path": st.column_config.ImageColumn("Photo"),
            "image_description": None,
        },
    )

    selected_product_id = st.selectbox(
        "Select product",
        [str(product["product_id"]) for product in products],
    )
    selected_product = product_service.get_product_by_id(selected_product_id, store_id) or {}

    with st.expander("Edit selected product", expanded=False):
        current_image_path = selected_product.get("image_path") or ""
        if current_image_path:
            absolute_image_path = BASE_DIR / current_image_path
            if absolute_image_path.exists():
                st.image(str(absolute_image_path), caption="Current product photo", width=160)
        with st.form("edit_product_form"):
            name = st.text_input("Name", value=selected_product.get("name", ""))
            barcode = st.text_input("Barcode", value=selected_product.get("barcode") or "")
            price = st.number_input(
                "Price",
                min_value=0.0,
                value=float(selected_product.get("price") or 0),
                step=1000.0,
            )
            description = st.text_area("Short description", value=selected_product.get("description") or "")
            replacement_image = st.file_uploader(
                "Replace product photo",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=False,
            )
            remove_image = st.checkbox("Remove photo")
            if replacement_image is not None:
                st.image(replacement_image, caption="New photo preview", width=140)
            if st.form_submit_button("Update product", use_container_width=True):
                image_path = selected_product.get("image_path") or ""
                image_description = selected_product.get("image_description") or ""
                image_storage = ImageStorageService()
                if remove_image:
                    image_storage.delete_image(image_path)
                    image_path = ""
                    image_description = ""
                elif replacement_image is not None:
                    image_storage.delete_image(image_path)
                    image_path = image_storage.save_product_image(
                        replacement_image,
                        store_id,
                        int(selected_product["id"]),
                    )
                    image_description = AIService().describe_image(image_path)
                product_service.update_product(
                    store_id,
                    selected_product_id,
                    name,
                    barcode,
                    price,
                    description,
                    image_path=image_path,
                    image_description=image_description,
                )
                st.success("Product updated.")
                st.rerun()

    if st.button("Delete selected product", use_container_width=True):
        ImageStorageService().delete_image(selected_product.get("image_path"))
        product_service.delete_product(selected_product_id, store_id)
        st.success("Product deleted.")
        st.rerun()


def _render_product_import(store_id: int, product_service: ProductService) -> None:
    st.markdown("**Import products**")
    uploaded_file = st.file_uploader(
        "Upload CSV or XLSX product database",
        type=["csv", "xlsx"],
        accept_multiple_files=False,
        key="product_database_import_file",
    )
    if uploaded_file is None:
        return

    import_service = ProductImportService(product_service)
    preview = import_service.parse_file(uploaded_file)

    if preview.errors:
        for error in preview.errors:
            st.error(error)
        if not preview.rows:
            return

    st.caption(f"Rows detected: {len(preview.rows)}")
    st.dataframe(preview.rows[:20], hide_index=True, use_container_width=True)
    if "image_url" in preview.rows[0]:
        st.info("Image URL import is not supported for downloading yet. URLs are stored as references only.")

    if st.button("Import products", use_container_width=True):
        if preview.errors:
            st.error("Fix file-level validation errors before importing.")
            return

        result = import_service.import_rows(store_id, preview.rows)
        st.success(
            f"Import finished. Products added: {result.added}; "
            f"updated: {result.updated}; rows skipped: {result.skipped}."
        )
        if result.errors:
            with st.expander("Validation errors and notes", expanded=True):
                for error in result.errors:
                    st.write(f"- {error}")


def _render_analytics(
    current_user: dict,
    store_service: StoreService,
    analytics_service: AnalyticsService,
) -> None:
    profile = _require_profile(current_user, store_service)
    if profile is None:
        return

    st.subheader("Product Analytics")
    analytics = analytics_service.get_store_analytics(int(profile["id"]))
    st.metric("Total product-related questions", analytics["total"])

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Top mentioned products**")
        st.dataframe(analytics["top_mentioned"], hide_index=True, use_container_width=True)
    with col_b:
        st.markdown("**Top recommended products**")
        st.dataframe(analytics["top_recommended"], hide_index=True, use_container_width=True)

    st.markdown("**Recent related queries**")
    st.dataframe(analytics["recent_queries"], hide_index=True, use_container_width=True)


def _render_store_assistant(
    current_user: dict,
    store_service: StoreService,
    store_assistant_service: StoreAssistantService,
) -> None:
    profile = _require_profile(current_user, store_service)
    if profile is None:
        return

    st.subheader("Store Assistant")
    st.caption("Internal helper for store data. It is not part of the public 3-agent customer network.")

    pending_action = st.session_state.get("store_assistant_pending_action")
    if pending_action:
        st.warning(st.session_state.get("store_assistant_pending_message", "Confirm this change?"))
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            if st.button("Confirm", use_container_width=True):
                result = store_assistant_service.confirm(pending_action, current_user, profile)
                st.session_state["store_assistant_response"] = result
                st.session_state.pop("store_assistant_pending_action", None)
                st.session_state.pop("store_assistant_pending_message", None)
                st.rerun()
        with cancel_col:
            if st.button("Cancel", use_container_width=True):
                st.session_state["store_assistant_response"] = "Canceled."
                st.session_state.pop("store_assistant_pending_action", None)
                st.session_state.pop("store_assistant_pending_message", None)
                st.rerun()

    command = st.text_input(
        "Store command",
        placeholder="Change price of product P001 to 145000",
    )
    if st.button("Ask Store Assistant", use_container_width=True):
        result = store_assistant_service.handle_command(command, current_user, profile)
        st.session_state["store_assistant_response"] = result["message"]
        if result["pending_action"]:
            st.session_state["store_assistant_pending_action"] = result["pending_action"]
            st.session_state["store_assistant_pending_message"] = result["message"]
        st.rerun()

    response = st.session_state.get("store_assistant_response")
    if response:
        st.info(response)

    with st.expander("Examples", expanded=False):
        st.write("Change price of product P001 to 145000")
        st.write("Update description of Laptop Pro and add that it is suitable for video editing")
        st.write("Show all products cheaper than 200000")
        st.write("Change my store address to Almaty, Abay Avenue 10")
        st.write("Add website link https://example.com")
        st.write("Which products are getting the most questions?")
        st.write("Show recent queries related to my products")


def _require_profile(current_user: dict, store_service: StoreService) -> dict | None:
    profile = store_service.get_profile(current_user["id"])
    if profile is None:
        st.warning("Create your Store Profile first.")
        return None
    return profile
