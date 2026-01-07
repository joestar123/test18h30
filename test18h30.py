# --- CỘT 2: CẤU HÌNH QUÉT (ĐÃ SỬA LỖI TRÔI GIỜ) ---
    with col2:
        st.subheader("2. Cấu hình quét")
        
        start_date = st.date_input("🚀 Ngày bắt đầu:", value=datetime.now().date())
        
        # --- FIX: DÙNG SESSION STATE ĐỂ GIỮ GIỜ CỐ ĐỊNH ---
        # Chỉ lấy giờ hiện tại MỘT LẦN khi mới mở web
        if "saved_time" not in st.session_state:
            st.session_state.saved_time = datetime.now().strftime("%H:%M:%S")

        col_h, col_m = st.columns([2, 1])
        with col_h:
            # Dùng key="saved_time" để liên kết với bộ nhớ, không bị reset khi Enter
            start_time_str = st.text_input(
                "Giờ (HH:MM:SS):", 
                key="saved_time", 
                help="Nhập chính xác giờ phút giây (ví dụ: 09:30:00)"
            )
        with col_m:
            hours_to_scan = st.number_input("Số giờ:", min_value=0.5, value=1.0, step=0.5)

        # Xử lý input thời gian
        try:
            t = datetime.strptime(start_time_str, "%H:%M:%S").time()
            start_scan_time = datetime.combine(start_date, t)
        except ValueError:
            st.error("❌ Sai định dạng! Hãy nhập: 10:30:00")
            st.stop()
        
        st.caption(f"🏁 Kết thúc: {(start_scan_time + timedelta(hours=hours_to_scan)).strftime('%H:%M:%S %d/%m')}")

        # Khoảng cách nhỏ
        st.write("")
        run_btn = st.button("BẮT ĐẦU QUÉT NGAY", type="primary")