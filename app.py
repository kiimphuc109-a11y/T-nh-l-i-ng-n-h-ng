import streamlit as st
import pandas as pd
import io

# =====================================================
# CẤU HÌNH TRANG
# =====================================================

st.set_page_config(
    page_title="Ứng dụng tính khoản vay",
    page_icon="🏦",
    layout="wide"
)

# =====================================================
# TIÊU ĐỀ
# =====================================================

st.title("🏦 ỨNG DỤNG TÍNH KHOẢN VAY NGÂN HÀNG")
st.subheader("Tính gốc, lãi và lập lịch trả nợ hàng tháng")

st.info(
    "Ứng dụng mô phỏng khoản vay phục vụ mục đích học tập. "
    "Kết quả thực tế có thể khác tùy chính sách của từng ngân hàng."
)

# =====================================================
# SIDEBAR - THÔNG TIN KHÁCH HÀNG
# =====================================================

st.sidebar.header("👤 Thông tin khách hàng")

customer_name = st.sidebar.text_input(
    "Họ và tên"
)

phone = st.sidebar.text_input(
    "Số điện thoại"
)

cccd = st.sidebar.text_input(
    "CMND/CCCD"
)

income = st.sidebar.number_input(
    "💵 Thu nhập hàng tháng (VNĐ)",
    min_value=0,
    value=10000000,
    step=500000,
    format="%d"
)

# =====================================================
# THÔNG TIN KHOẢN VAY
# =====================================================

st.header("📋 1. Thông tin khoản vay")

col1, col2 = st.columns(2)

with col1:

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

with col2:

    interest_rate = st.number_input(
        "📈 Lãi suất (%/năm)",
        min_value=0.0,
        max_value=50.0,
        value=10.0,
        step=0.1
    )

    loan_purpose = st.selectbox(
        "🎯 Mục đích / sản phẩm vay",
        [
            "Vay mua nhà",
            "Vay mua ô tô",
            "Vay tiêu dùng",
            "Vay kinh doanh",
            "Vay sửa chữa nhà",
            "Vay học tập",
            "Vay khác"
        ]
    )

# =====================================================
# PHƯƠNG THỨC TRẢ NỢ
# =====================================================

st.header("🧮 2. Phương thức trả nợ")

method = st.radio(
    "Chọn phương thức tính:",
    [
        "Dư nợ giảm dần - Gốc chia đều",
        "Trả đều hàng tháng - Niên kim"
    ],
    horizontal=True
)

# =====================================================
# TÍNH TOÁN
# =====================================================

monthly_rate = interest_rate / 100 / 12

schedule = []

remaining_principal = float(loan_amount)

total_interest = 0
total_payment = 0

# =====================================================
# PHƯƠNG ÁN 1
# =====================================================

if method == "Dư nợ giảm dần - Gốc chia đều":

    principal_monthly = (
        loan_amount / loan_term
    )

    for month in range(1, loan_term + 1):

        beginning_balance = remaining_principal

        interest = (
            beginning_balance
            * monthly_rate
        )

        principal = principal_monthly

        if month == loan_term:
            principal = beginning_balance

        payment = principal + interest

        remaining_principal -= principal

        if remaining_principal < 0:
            remaining_principal = 0

        total_interest += interest
        total_payment += payment

        schedule.append({
            "Tháng": month,
            "Dư nợ đầu kỳ": beginning_balance,
            "Gốc phải trả": principal,
            "Lãi phải trả": interest,
            "Tổng phải trả": payment,
            "Dư nợ cuối kỳ": remaining_principal
        })

# =====================================================
# PHƯƠNG ÁN 2
# =====================================================

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
                (1 + monthly_rate) ** loan_term
                - 1
            )
        )

    for month in range(1, loan_term + 1):

        beginning_balance = remaining_principal

        interest = (
            beginning_balance
            * monthly_rate
        )

        principal = (
            monthly_payment - interest
        )

        if month == loan_term:
            principal = beginning_balance

        payment = principal + interest

        remaining_principal -= principal

        if remaining_principal < 0:
            remaining_principal = 0

        total_interest += interest
        total_payment += payment

        schedule.append({
            "Tháng": month,
            "Dư nợ đầu kỳ": beginning_balance,
            "Gốc phải trả": principal,
            "Lãi phải trả": interest,
            "Tổng phải trả": payment,
            "Dư nợ cuối kỳ": remaining_principal
        })

# =====================================================
# DATAFRAME
# =====================================================

df = pd.DataFrame(schedule)

# =====================================================
# KẾT QUẢ TỔNG QUAN
# =====================================================

st.header("📊 3. Kết quả khoản vay")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Tiền vay",
        f"{loan_amount:,.0f} VNĐ"
    )

with col2:
    st.metric(
        "📈 Tổng tiền lãi",
        f"{total_interest:,.0f} VNĐ"
    )

with col3:
    st.metric(
        "💵 Tổng phải trả",
        f"{total_payment:,.0f} VNĐ"
    )

with col4:
    st.metric(
        "📅 Thời hạn",
        f"{loan_term} tháng"
    )

# =====================================================
# THÁNG ĐẦU TIÊN
# =====================================================

st.subheader("💳 Khoản phải trả tháng đầu tiên")

first_month = df.iloc[0]

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
        "Tổng thanh toán",
        f"{first_month['Tổng phải trả']:,.0f} VNĐ"
    )

# =====================================================
# ĐÁNH GIÁ KHẢ NĂNG TRẢ NỢ
# =====================================================

st.header("⚠️ 4. Đánh giá khả năng trả nợ")

monthly_payment = first_month["Tổng phải trả"]

if income > 0:

    debt_ratio = (
        monthly_payment / income
    ) * 100

    st.write(
        f"Thu nhập hàng tháng: "
        f"**{income:,.0f} VNĐ**"
    )

    st.write(
        f"Khoản trả tháng đầu: "
        f"**{monthly_payment:,.0f} VNĐ**"
    )

    st.write(
        f"Tỷ lệ trả nợ/thu nhập: "
        f"**{debt_ratio:.2f}%**"
    )

    if debt_ratio <= 30:

        st.success(
            "✅ Mức trả nợ tương đối thấp "
            "so với thu nhập."
        )

    elif debt_ratio <= 50:

        st.warning(
            "⚠️ Khoản trả nợ chiếm tỷ lệ khá cao "
            "so với thu nhập."
        )

    else:

        st.error(
            "❌ Khoản trả nợ chiếm tỷ lệ cao "
            "so với thu nhập. Cần cân nhắc khả năng tài chính."
        )

# =====================================================
# BIỂU ĐỒ
# =====================================================

st.header("📈 5. Biểu đồ khoản vay")

chart_data = df[
    [
        "Tháng",
        "Gốc phải trả",
        "Lãi phải trả"
    ]
].set_index("Tháng")

st.bar_chart(chart_data)

st.subheader("📉 Dư nợ còn lại")

balance_chart = df[
    [
        "Tháng",
        "Dư nợ cuối kỳ"
    ]
].set_index("Tháng")

st.line_chart(balance_chart)

# =====================================================
# LỊCH TRẢ NỢ
# =====================================================

st.header("📅 6. Lịch trả nợ")

display_df = df.copy()

money_columns = [
    "Dư nợ đầu kỳ",
    "Gốc phải trả",
    "Lãi phải trả",
    "Tổng phải trả",
    "Dư nợ cuối kỳ"
]

for column in money_columns:

    display_df[column] = display_df[column].apply(
        lambda x: f"{x:,.0f} VNĐ"
    )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# SO SÁNH PHƯƠNG ÁN
# =====================================================

st.header("⚖️ 7. So sánh phương án trả nợ")

def calculate_annuity():

    if monthly_rate == 0:

        payment = loan_amount / loan_term

    else:

        payment = (
            loan_amount
            * monthly_rate
            * (1 + monthly_rate) ** loan_term
            /
            (
                (1 + monthly_rate) ** loan_term - 1
            )
        )

    balance = loan_amount
    interest_total = 0

    for _ in range(loan_term):

        interest = balance * monthly_rate

        principal = payment - interest

        balance -= principal

        interest_total += interest

    return payment, interest_total


def calculate_declining():

    balance = loan_amount

    principal = loan_amount / loan_term

    interest_total = 0

    first_payment = 0

    for month in range(1, loan_term + 1):

        interest = balance * monthly_rate

        payment = principal + interest

        if month == 1:
            first_payment = payment

        interest_total += interest

        balance -= principal

    return first_payment, interest_total


declining_first, declining_interest = (
    calculate_declining()
)

annuity_payment, annuity_interest = (
    calculate_annuity()
)

comparison = pd.DataFrame({
    "Phương án": [
        "Dư nợ giảm dần",
        "Trả đều hàng tháng"
    ],
    "Tiền trả tháng đầu": [
        declining_first,
        annuity_payment
    ],
    "Tổng tiền lãi": [
        declining_interest,
        annuity_interest
    ]
})

comparison_display = comparison.copy()

comparison_display[
    "Tiền trả tháng đầu"
] = comparison_display[
    "Tiền trả tháng đầu"
].apply(
    lambda x: f"{x:,.0f} VNĐ"
)

comparison_display[
    "Tổng tiền lãi"
] = comparison_display[
    "Tổng tiền lãi"
].apply(
    lambda x: f"{x:,.0f} VNĐ"
)

st.dataframe(
    comparison_display,
    use_container_width=True,
    hide_index=True
)

if declining_interest < annuity_interest:

    st.success(
        "💡 Với khoản vay hiện tại, "
        "phương án dư nợ giảm dần có tổng tiền lãi thấp hơn."
    )

else:

    st.info(
        "💡 Hai phương án đã được tính để bạn "
        "so sánh tổng chi phí khoản vay."
    )

# =====================================================
# XUẤT FILE CSV
# =====================================================

st.header("📥 8. Xuất lịch trả nợ")

csv_data = df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 Tải lịch trả nợ CSV",
    data=csv_data,
    file_name="lich_tra_no_ngan_hang.csv",
    mime="text/csv",
    use_container_width=True
)

# =====================================================
# PHIẾU THÔNG TIN KHOẢN VAY
# =====================================================

st.subheader("📄 Phiếu thông tin khoản vay")

loan_info = f"""
========================================
       PHIẾU THÔNG TIN KHOẢN VAY
========================================

Khách hàng: {customer_name}
Số điện thoại: {phone}
CMND/CCCD: {cccd}

Mục đích vay: {loan_purpose}

Số tiền vay:
{loan_amount:,.0f} VNĐ

Thời hạn:
{loan_term} tháng

Lãi suất:
{interest_rate:.2f}%/năm

Phương thức:
{method}

Tổng tiền lãi:
{total_interest:,.0f} VNĐ

Tổng tiền phải trả:
{total_payment:,.0f} VNĐ

Khoản trả tháng đầu:
{monthly_payment:,.0f} VNĐ

========================================
"""

loan_file = io.BytesIO()
loan_file.write(
    loan_info.encode("utf-8")
)
loan_file.seek(0)

st.download_button(
    "📄 Tải phiếu thông tin khoản vay",
    data=loan_file,
    file_name="phieu_khoan_vay.txt",
    mime="text/plain",
    use_container_width=True
)

# =====================================================
# CHATBOT
# =====================================================

st.header("🤖 9. Chatbot hỗ trợ")

st.write(
    "Bạn có thể hỏi chatbot về khoản vay của mình."
)

question = st.text_input(
    "💬 Nhập câu hỏi",
    placeholder="Ví dụ: Tháng đầu tôi phải trả bao nhiêu?"
)

if question:

    q = question.lower()

    if (
        "tháng đầu" in q
        or "tháng 1" in q
    ):

        st.success(
            f"💳 Tháng đầu tiên bạn phải trả "
            f"**{monthly_payment:,.0f} VNĐ**."
        )

    elif (
        "tổng lãi" in q
        or "tiền lãi" in q
    ):

        st.success(
            f"📈 Tổng tiền lãi dự kiến là "
            f"**{total_interest:,.0f} VNĐ**."
        )

    elif (
        "tổng tiền" in q
        or "tổng phải trả" in q
    ):

        st.success(
            f"💰 Tổng số tiền phải trả là "
            f"**{total_payment:,.0f} VNĐ**."
        )

    elif (
        "số tiền vay" in q
        or "vay bao nhiêu" in q
    ):

        st.info(
            f"💰 Bạn đang nhập khoản vay "
            f"**{loan_amount:,.0f} VNĐ**."
        )

    elif "lãi suất" in q:

        st.info(
            f"📈 Lãi suất hiện tại là "
            f"**{interest_rate:.2f}%/năm**."
        )

    elif (
        "thời hạn" in q
        or "bao lâu" in q
    ):

        st.info(
            f"📅 Thời hạn khoản vay là "
            f"**{loan_term} tháng**."
        )

    elif (
        "mục đích" in q
        or "sản phẩm" in q
    ):

        st.info(
            f"🎯 Khoản vay đang được chọn cho "
            f"mục đích **{loan_purpose}**."
        )

    elif (
        "dư nợ giảm dần" in q
        or "dư nợ" in q
    ):

        st.info(
            "📉 Dư nợ giảm dần là phương pháp "
            "tính lãi dựa trên số tiền gốc còn lại. "
            "Khi dư nợ giảm, tiền lãi cũng giảm."
        )

    elif (
        "cách tính" in q
        or "công thức" in q
    ):

        st.info(
            "🧮 App đang hỗ trợ 2 phương thức: "
            "dư nợ giảm dần - gốc chia đều và "
            "trả đều hàng tháng theo phương pháp niên kim."
        )

    elif (
        "chào" in q
        or "hello" in q
    ):

        st.success(
            "👋 Xin chào! Tôi có thể hỗ trợ bạn "
            "về khoản vay, tiền gốc, tiền lãi, "
            "thời hạn và lịch trả nợ."
        )

    else:

        st.warning(
            "🤔 Tôi chưa hiểu câu hỏi. "
            "Bạn có thể hỏi về: tiền vay, tiền lãi, "
            "tổng tiền phải trả, tháng đầu tiên, "
            "lãi suất, thời hạn hoặc dư nợ."
        )

# =====================================================
# LÀM LẠI
# =====================================================

st.markdown("---")

if st.button(
    "🔄 TẠO KHOẢN VAY MỚI",
    use_container_width=True
):

    st.rerun()

# =====================================================
# CHÂN TRANG
# =====================================================

st.markdown("---")

st.caption(
    "🏦 Ứng dụng mô phỏng tính khoản vay ngân hàng "
    "– Phục vụ mục đích học tập"
)
