import streamlit as st
import pandas as pd
# ==========================================
# CẤU HÌNH TRANG
# ==========================================
st.set_page_config(
    page_title="Tính khoản vay ngân hàng",
    page_icon="🏦",
    layout="centered"
)
# ==========================================
# TIÊU ĐỀ
# ==========================================
st.title("🏦 APP TÍNH KHOẢN VAY NGÂN HÀNG")
st.subheader("Tính số tiền gốc và lãi phải trả hàng tháng")
st.write(
    "Nhập thông tin khoản vay để hệ thống tính "
    "lịch trả nợ hàng tháng."
)
st.markdown("---")
# ==========================================
# THÔNG TIN KHOẢN VAY
# ==========================================
st.subheader("📋 Thông tin khoản vay")
loan_amount = st.number_input(
    "💰 Số tiền vay (VNĐ)",
    min_value=1000000,
    value=100000000,
    step=1000000,
    format="%d"
)
loan_term = st.number_input(
    "📅 Thời hạn vay (tháng)",
    min_value=1,
    max_value=360,
    value=12,
    step=1
)
interest_rate = st.number_input(
    "📈 Lãi suất cho vay (%/năm)",
    min_value=0.0,
    max_value=50.0,
    value=10.0,
    step=0.1
)
loan_purpose = st.selectbox(
    "🎯 Mục đích / sản phẩm cho vay",
    [
        "Vay mua nhà",
        "Vay mua ô tô",
        "Vay tiêu dùng",
        "Vay kinh doanh",
        "Vay sửa chữa nhà",
        "Vay học tập",
        "Khác"
    ]
)
# ==========================================
# PHƯƠNG THỨC TÍNH
# ==========================================
st.subheader("🧮 Phương thức tính")
method = st.selectbox(
    "Chọn phương thức trả nợ",
    [
        "Dư nợ giảm dần - Gốc chia đều",
        "Trả đều hàng tháng (niên kim)"
    ]
)
# ==========================================
# NÚT TÍNH TOÁN
# ==========================================
if st.button(
    "🧮 TÍNH KHOẢN VAY",
    use_container_width=True
):
    # Lãi suất tháng
    monthly_rate = interest_rate / 100 / 12
    # ======================================
    # PHƯƠNG ÁN 1:
    # DƯ NỢ GIẢM DẦN - GỐC CHIA ĐỀU
    # ======================================
    if method == "Dư nợ giảm dần - Gốc chia đều":
        principal_monthly = (
            loan_amount / loan_term
        )
        remaining_principal = loan_amount
        schedule = []
        total_interest = 0
        total_payment = 0
        for month in range(1, loan_term + 1):
            interest = (
                remaining_principal
                * monthly_rate
            )
            principal = principal_monthly
            # Tháng cuối xử lý phần lẻ
            if month == loan_term:
                principal = remaining_principal
            payment = principal + interest
            remaining_principal -= principal
            if remaining_principal < 0:
                remaining_principal = 0
            total_interest += interest
            total_payment += payment
            schedule.append({
                "Tháng": month,
                "Dư nợ đầu kỳ": round(
                    remaining_principal + principal
                ),
                "Gốc phải trả": round(principal),
                "Lãi phải trả": round(interest),
                "Tổng phải trả": round(payment),
                "Dư nợ cuối kỳ": round(
                    remaining_principal
                )
            })
    # ======================================
    # PHƯƠNG ÁN 2:
    # TRẢ ĐỀU HÀNG THÁNG
    # ======================================
    else:
        if monthly_rate == 0:
            monthly_payment = (
                loan_amount / loan_term
            )
        else:
            monthly_payment = (
                loan_amount
                * monthly_rate
                * (1 + monthly_rate) ** loan_term
                /
                (
                    (1 + monthly_rate)
                    ** loan_term
                    - 1
                )
            )
        remaining_principal = loan_amount
        schedule = []
        total_interest = 0
        total_payment = 0
        for month in range(1, loan_term + 1):
            interest = (
                remaining_principal
                * monthly_rate
            )
            principal = (
                monthly_payment - interest
            )
            if month == loan_term:
                principal = remaining_principal
                payment = principal + interest
            else:
                payment = monthly_payment
            remaining_principal -= principal
            if remaining_principal < 0:
                remaining_principal = 0
            total_interest += interest
            total_payment += payment
            schedule.append({
                "Tháng": month,
                "Dư nợ đầu kỳ": round(
                    remaining_principal + principal
                ),
                "Gốc phải trả": round(principal),
                "Lãi phải trả": round(interest),
                "Tổng phải trả": round(payment),
                "Dư nợ cuối kỳ": round(
                    remaining_principal
                )
            })
    # ======================================
    # KẾT QUẢ TỔNG QUAN
    # ======================================
    st.markdown("---")
    st.subheader("📊 KẾT QUẢ KHOẢN VAY")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "💰 Số tiền vay",
            f"{loan_amount:,.0f} VNĐ"
        )
        st.metric(
            "📈 Tổng tiền lãi",
            f"{total_interest:,.0f} VNĐ"
        )
    with col2:
        st.metric(
            "💵 Tổng tiền phải trả",
            f"{total_payment:,.0f} VNĐ"
        )
        st.metric(
            "📅 Thời hạn",
            f"{loan_term} tháng"
        )
    st.info(
        f"🎯 Mục đích vay: **{loan_purpose}**"
    )
    st.write(
        f"📌 Lãi suất: **{interest_rate:.2f}%/năm**"
    )
    st.write(
        f"📌 Phương thức: **{method}**"
    )
    # ======================================
    # KHOẢN THANH TOÁN THÁNG ĐẦU
    # ======================================
    first_month = schedule[0]
    st.markdown("---")
    st.subheader("💳 Tháng đầu tiên")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Gốc",
            f"{first_month['Gốc phải trả']:,.0f} VNĐ"
        )
    with col2:
        st.metric(
            "Lãi",
            f"{first_month['Lãi phải trả']:,.0f} VNĐ"
        )
    with col3:
        st.metric(
            "Tổng trả",
            f"{first_month['Tổng phải trả']:,.0f} VNĐ"
        )
    # ======================================
    # LỊCH TRẢ NỢ
    # ======================================
    st.markdown("---")
    st.subheader("📅 Lịch trả nợ hàng tháng")
    df = pd.DataFrame(schedule)
    # Định dạng tiền
    df_display = df.copy()
    money_columns = [
        "Dư nợ đầu kỳ",
        "Gốc phải trả",
        "Lãi phải trả",
        "Tổng phải trả",
        "Dư nợ cuối kỳ"
    ]
    for column in money_columns:
        df_display[column] = df_display[column].apply(
            lambda x: f"{x:,.0f} VNĐ"
        )
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    # ======================================
    # TỔNG KẾT
    # ======================================
    st.markdown("---")
    st.subheader("📌 Tổng kết")
    st.write(
        f"• Số tiền vay: **{loan_amount:,.0f} VNĐ**"
    )
    st.write(
        f"• Thời hạn vay: **{loan_term} tháng**"
    )
    st.write(
        f"• Lãi suất: **{interest_rate:.2f}%/năm**"
    )
    st.write(
        f"• Tổng tiền gốc: **{loan_amount:,.0f} VNĐ**"
    )
    st.write(
        f"• Tổng tiền lãi: **{total_interest:,.0f} VNĐ**"
    )
    st.write(
        f"• Tổng số tiền phải trả: "
        f"**{total_payment:,.0f} VNĐ**"
    )
    # ======================================
    # TẢI FILE EXCEL/CSV
    # ======================================
    csv = df.to_csv(
        index=False
    ).encode("utf-8-sig")
    st.download_button(
        label="📥 Tải lịch trả nợ",
        data=csv,
        file_name="lich_tra_no.csv",
        mime="text/csv",
        use_container_width=True
    )
