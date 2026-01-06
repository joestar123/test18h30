import streamlit as st
import random
import time
from datetime import datetime, timedelta, date

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Tool Tra Cứu Số Học Phong Thủy",
    page_icon="🔮",
    layout="wide"
)

# --- 1. IMPORT THƯ VIỆN ÂM LỊCH ---
try:
    from lunardate import LunarDate
    HAS_LUNAR_LIB = True
except ImportError:
    HAS_LUNAR_LIB = False

# --- 2. CÁC HÀM LOGIC CỐT LÕI (GIỮ NGUYÊN TỪ CODE GỐC) ---

def get_lunar_year_number(date_obj):
    """Lấy năm âm lịch"""
    if HAS_LUNAR_LIB:
        lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
        return lunar.year
    else:
        return date_obj.year

def calculate_menh_nien(year):
    """Tính mệnh niên dựa trên năm âm lịch"""
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
    """Lấy ngũ hành của con số"""
    last_digit = int(number_str[-1])
    if last_digit in [1, 6]: return "Thủy"
    if last_digit in [2, 7]: return "Hỏa"
    if last_digit in [3, 8]: return "Mộc"
    if last_digit in [4, 9]: return "Kim"
    return "Thổ"

def check_compatibility(user_menh, num_menh):
    """Kiểm tra tương sinh/tương hợp"""
    tuong_sinh = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
    if user_menh == num_menh: return True # Bình Hòa
    if tuong_sinh.get(num_menh) == user_menh: return True # Tương Sinh
    return False

# --- 3. GIAO DIỆN NGƯỜI DÙNG (STREAMLIT) ---

def main():
    st.title("🔮 Tool Tra Cứu Số Học Phong Thủy (Streamlit Version)")
    st.markdown("---")

    # Kiểm tra thư viện
    if not HAS_LUNAR_LIB:
        st.warning("⚠️ Chưa cài thư viện `lunardate`. Kết quả tính Mệnh có thể không chính xác nếu ngày sinh rơi vào tháng đầu năm Dương lịch.")
    
    col1, col2 = st.columns(2)

    with col1:
        st.header("1. Thông tin cá nhân")
        # Nhập ngày sinh
        dob_input = st.date_input("Ngày sinh của bạn:", value=date(1996, 5, 20), min_value=date(1900, 1, 1))
        
        # Tính toán mệnh ngay lập tức để hiển thị
        lunar_year = get_lunar_year_number(dob_input)
        user_menh = calculate_menh_nien(lunar_year)
        st.info(f"🎭 **Mệnh của bạn:** {user_menh} (Năm âm: {lunar_year})")

        st.header("2. Thông tin Seed")
        # Ngày đích
        target_date_input = st.date_input("Ngày đích (Target Date):", value=datetime.now().date())
        
        # Số yêu thích
        fav_str = st.text_input("Các con số yêu thích (cách nhau dấu phẩy):", placeholder="Ví dụ: 79, 39")
        
        # Xử lý số yêu thích
        fav_list_raw = fav_str.split(',')
        valid_favs = []
        for f in fav_list_raw:
            f = f.strip()
            if f.isdigit() and len(f) == 2:
                valid_favs.append(f)
        
        if valid_favs:
            st.caption(f"✅ Các số hợp lệ dùng tính Seed: {valid_favs}")
        else:
            st.caption("⚠️ Chưa có số hợp lệ (hoặc để trống).")

    with col2:
        st.header("3. Cấu hình quét")
        
        # Chọn ngày giờ bắt đầu quét
        start_date = st.date_input("Ngày bắt đầu quét:", value=datetime.now().date())
        start_time_val = st.time_input("Giờ bắt đầu quét:", value=datetime.now().time())
        
        # Ghép thành datetime
        start_scan_time = datetime.combine(start_date, start_time_val)
        
        # Thời gian quét
        hours_to_scan = st.number_input("Thời gian quét (giờ):", min_value=0.1, value=1.0, step=0.5)
        
        st.markdown(f"**Thời gian kết thúc:** { (start_scan_time + timedelta(hours=hours_to_scan)).strftime('%H:%M:%S %d/%m/%Y') }")

        # Nút chạy
        run_btn = st.button("🚀 BẮT ĐẦU QUÉT", type="primary")

    # --- 4. XỬ LÝ KHI BẤM NÚT ---
    if run_btn:
        st.markdown("---")
        st.subheader("📊 Kết quả phân tích")
        
        end_time = start_scan_time + timedelta(hours=hours_to_scan)
        total_seconds = int((end_time - start_scan_time).total_seconds())
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        found_results = []
        
        # Chuẩn bị string cố định cho seed
        dob_str = dob_input.strftime("%d%m%Y")
        target_str = target_date_input.strftime("%d%m%Y")
        fav_part = "".join(valid_favs)
        
        start_perf = time.time()
        
        # VÒNG LẶP (Optimize: Không in mỗi giây, chỉ lưu kết quả)
        for i in range(total_seconds):
            future_time = start_scan_time + timedelta(seconds=i)
            
            # Cập nhật progress bar mỗi 5% hoặc mỗi 2 giây thực tế để không lag UI
            if i % 1000 == 0: 
                prog = i / total_seconds
                progress_bar.progress(prog)
                status_text.text(f"⏳ Đang quét: {future_time.strftime('%H:%M:%S %d/%m')} ...")

            # --- LOGIC TẠO SEED ---
            time_str = future_time.strftime('%d%m%Y%H%M%S') 
            seed_val = f"{dob_str}{target_str}{time_str}{fav_part}"
            
            random.seed(seed_val)
            
            # Sinh 5 số
            kq = [f"{random.randint(0,99):02d}" for _ in range(5)]
            
            # --- KIỂM TRA ĐIỀU KIỆN ---
            compatible_count = 0
            for num in kq:
                num_menh = get_number_element(num)
                if check_compatibility(user_menh, num_menh):
                    compatible_count += 1
            
            if compatible_count == 5:
                current_second = future_time.second
                has_matching_second = any(int(num) == current_second for num in kq)
                
                if has_matching_second:
                    found_results.append({
                        "Thời gian": future_time.strftime('%H:%M:%S %d/%m/%Y'),
                        "Bộ số": ", ".join(kq),
                        "Giây trùng": current_second
                    })
        
        # Hoàn thành
        progress_bar.progress(100)
        status_text.text("✅ Đã hoàn tất!")
        
        duration = time.time() - start_perf
        st.success(f"Quét xong {total_seconds} mốc thời gian trong {duration:.2f}s thực tế.")
        
        if len(found_results) > 0:
            st.write(f"🎉 Tìm thấy **{len(found_results)}** kết quả thỏa mãn:")
            st.dataframe(found_results, use_container_width=True)
            
            if start_scan_time > datetime.now():
                st.info("💡 MẸO: Vì độ trễ mạng, hãy thao tác sớm hơn 1-2 giây so với thời gian hiển thị.")
        else:
            st.error("❌ Không tìm thấy kết quả nào trong khoảng thời gian này.")

if __name__ == "__main__":
    main()