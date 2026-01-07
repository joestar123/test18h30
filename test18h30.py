import streamlit as st
import random
import time
from datetime import datetime, timedelta, date

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Tool Số Học Phong Thủy",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS TÙY CHỈNH (CHO ĐẸP HƠN TRÊN MOBILE) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        font-weight: bold;
        height: 3em;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. IMPORT THƯ VIỆN ÂM LỊCH ---
try:
    from lunardate import LunarDate
    HAS_LUNAR_LIB = True
except ImportError:
    HAS_LUNAR_LIB = False

# --- 2. CÁC HÀM LOGIC CỐT LÕI (GIỮ NGUYÊN LOGIC GỐC) ---

def get_lunar_year_number(date_obj):
    if HAS_LUNAR_LIB:
        lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
        return lunar.year
    else:
        return date_obj.year

def calculate_menh_nien(year):
    can_values = {4:1, 5:1, 6:2, 7:2, 8:3, 9:3, 0:4, 1:4, 2:5, 3:5}
    can_val = can_values[year % 10]
    chi_mod = year % 12
    if chi_mod in [4, 5, 10, 11]: chi_val = 0
    elif chi_mod in [6, 7, 0, 1]: chi_val = 1
    else: chi_val = 2
    total = can_val + chi_val
    if total > 5: total -= 5
    menh_map = {1: "Kim", 2: "Thủy", 3: "Hỏa", 4: "Thổ", 5: "Mộc"}
    return menh_map[total]

def get_number_element(number_str):
    last_digit = int(number_str[-1])
    if last_digit in [1, 6]: return "Thủy"
    if last_digit in [2, 7]: return "Hỏa"
    if last_digit in [3, 8]: return "Mộc"
    if last_digit in [4, 9]: return "Kim"
    return "Thổ"

def check_compatibility(user_menh, num_menh):
    tuong_sinh = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
    if user_menh == num_menh: return True # Bình Hòa
    if tuong_sinh.get(num_menh) == user_menh: return True # Tương Sinh
    return False

# --- 3. GIAO DIỆN CHÍNH ---

def main():
    st.title("🔮 Tool Tra Cứu Số Học (Mobile Optimized)")
    
    # Cảnh báo thư viện
    if not HAS_LUNAR_LIB:
        st.warning("⚠️ Chưa cài `lunardate`. Tính mệnh có thể sai lệch nhỏ.")
    
    # Chia cột (Trên mobile sẽ tự động xếp chồng lên nhau)
    col1, col2 = st.columns(2)

    # --- CỘT 1: THÔNG TIN CÁ NHÂN ---
    with col1:
        st.subheader("1. Thông tin")
        dob_input = st.date_input("📅 Ngày sinh:", value=date(1996, 5, 20), min_value=date(1900, 1, 1))
        
        # Tính mệnh
        lunar_year = get_lunar_year_number(dob_input)
        user_menh = calculate_menh_nien(lunar_year)
        st.info(f"🎭 Mệnh: **{user_menh}** (Năm âm: {lunar_year})")

        target_date_input = st.date_input("🎯 Ngày đích (Target):", value=datetime.now().date())
        
        fav_str = st.text_input("🔢 Số yêu thích (79, 39...):", placeholder="Ví dụ: 79, 39")
        
        # Xử lý số
        fav_list_raw = fav_str.split(',')
        valid_favs = []
        for f in fav_list_raw:
            f = f.strip()
            if f.isdigit() and len(f) == 2:
                valid_favs.append(f)
        
        if valid_favs:
            st.caption(f"✅ Seed numbers: {valid_favs}")

    # --- CỘT 2: CẤU HÌNH QUÉT (ĐÃ SỬA CHO MOBILE) ---
    with col2:
        st.subheader("2. Cấu hình quét")
        
        start_date = st.date_input("🚀 Ngày bắt đầu:", value=datetime.now().date())
        
        # --- FIX: DÙNG TEXT INPUT ĐỂ DỄ NHẬP GIỜ TRÊN MOBILE ---
        col_h, col_m = st.columns([2, 1])
        with col_h:
            now_str = datetime.now().strftime("%H:%M:%S")
            start_time_str = st.text_input("Giờ (HH:MM:SS):", value=now_str, help="Nhập chính xác giờ phút giây")
        with col_m:
            hours_to_scan = st.number_input("Số giờ:", min_value=0.5, value=1.0, step=0.5)

        # Xử lý input thời gian
        try:
            t = datetime.strptime(start_time_str, "%H:%M:%S").time()
            start_scan_time = datetime.combine(start_date, t)
        except ValueError:
            st.error("❌ Định dạng giờ sai. Ví dụ đúng: 10:30:00")
            st.stop()
        
        st.caption(f"🏁 Kết thúc: {(start_scan_time + timedelta(hours=hours_to_scan)).strftime('%H:%M:%S %d/%m')}")

        # Khoảng cách nhỏ
        st.write("")
        run_btn = st.button("BẮT ĐẦU QUÉT NGAY", type="primary")

    # --- 4. XỬ LÝ LOGIC ---
    if run_btn:
        st.divider()
        st.write(f"⏳ Đang xử lý từ **{start_scan_time.strftime('%H:%M:%S')}**...")
        
        # Tính toán
        end_time = start_scan_time + timedelta(hours=hours_to_scan)
        total_seconds = int((end_time - start_scan_time).total_seconds())
        
        # UI Progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        found_results = []
        
        # Chuẩn bị string cố định để tối ưu loop
        dob_str = dob_input.strftime("%d%m%Y")
        target_str = target_date_input.strftime("%d%m%Y")
        fav_part = "".join(valid_favs)
        
        start_perf = time.time()
        
        # --- LOOP TỐI ƯU ---
        # Không update UI mỗi giây để tránh lag
        update_step = max(1, total_seconds // 100) # Update mỗi 1%

        for i in range(total_seconds):
            # Update thanh tiến trình
            if i % update_step == 0:
                progress_bar.progress(i / total_seconds)
            
            future_time = start_scan_time + timedelta(seconds=i)
            
            # 1. Tạo Seed
            time_str = future_time.strftime('%d%m%Y%H%M%S') 
            seed_val = f"{dob_str}{target_str}{time_str}{fav_part}"
            
            random.seed(seed_val)
            
            # 2. Sinh 5 số
            kq = [f"{random.randint(0,99):02d}" for _ in range(5)]
            
            # 3. Check Mệnh (5/5 số phải hợp)
            compatible_count = 0
            for num in kq:
                num_menh = get_number_element(num)
                if check_compatibility(user_menh, num_menh):
                    compatible_count += 1
            
            if compatible_count == 5:
                # 4. Check Boss Mode (Số trùng giây)
                current_second = future_time.second
                has_matching_second = any(int(num) == current_second for num in kq)
                
                if has_matching_second:
                    found_results.append({
                        "Thời gian": future_time.strftime('%H:%M:%S %d/%m'),
                        "Bộ số": " - ".join(kq),
                        "Giây trùng": f"{current_second:02d}"
                    })

        # --- KẾT THÚC ---
        progress_bar.progress(100)
        status_text.text("✅ Hoàn tất!")
        
        duration = time.time() - start_perf
        
        if len(found_results) > 0:
            st.success(f"🎉 Tìm thấy {len(found_results)} kết quả (trong {duration:.2f}s)")
            
            # Hiển thị bảng kết quả đẹp
            st.dataframe(
                found_results, 
                use_container_width=True,
                column_config={
                    "Thời gian": st.column_config.TextColumn("Thời gian (Giờ/Ngày)"),
                    "Bộ số": st.column_config.TextColumn("Bộ số dự đoán"),
                    "Giây trùng": st.column_config.TextColumn("Giây khớp lệnh")
                }
            )
            
            if start_scan_time > datetime.now():
                st.warning("💡 LƯU Ý: Nên bấm nút trước 1-2 giây so với kết quả để trừ hao độ trễ mạng.")
        else:
            st.error("❌ Không tìm thấy kết quả nào phù hợp tiêu chí Boss Mode.")

if __name__ == "__main__":
    main()