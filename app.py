import streamlit as st
import pandas as pd
import io

# =========================================================
# CẤU HÌNH TRANG
# =========================================================

st.set_page_config(
    page_title="Ứng dụng tính khoản vay",
    page_icon="🏦",
    layout="wide"
)

# =========================================================
# TIÊU ĐỀ
# =========================================================

st.title("🏦 ỨNG DỤNG TÍNH KHOẢN VAY NGÂN HÀNG")
st.caption(
    "Tính gốc - lãi hàng tháng, đánh giá khả năng trả nợ "
    "và hỗ trợ tư vấn khoản vay bằng AI Gemini"
)

# =========================================================
# HÀM ĐỊNH DẠNG TIỀN
# =========================================================

def format_money(number):
    return f"{number:,.0f} VNĐ"


# =========================================================
# SIDEBAR - THÔNG TIN KHÁCH HÀNG
# =========================================================

st.sidebar.header("👤 THÔNG TIN KHÁCH HÀNG")

customer_name = st.sidebar.text_input(
    "Họ và tên",
    placeholder="Nhập họ tên"
)

phone = st.sidebar.text_input(
    "Số điện thoại",
    placeholder="Nhập số điện thoại"
)

cccd = st.sidebar.text_input(
    "CCCD",
    placeholder="Nhập số CCCD"
)

income = st.sidebar.number_input(
    "Thu nhập hàng tháng (VNĐ)",
    min_value=0,
    value=10000000,
    step=500000
)

# =========================================================
# THÔNG TIN KHOẢN VAY
# =========================================================

st.header("📋 THÔNG TIN KHOẢN VAY")

col1, col2 = st.columns(2)

with col1:

    loan_amount = st.number_input(
        "💵 Số tiền vay (VNĐ)",
        min_value=1000000,
        value=100000000,
        step=1000000
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
        max_value=100.0,
        value=10.0,
        step=0.1
    )

with col2:

    loan_purpose = st.selectbox(
        "🎯 Mục đích / sản phẩm vay",
        [
            "Vay mua nhà",
            "Vay mua ô tô",
            "Vay tiêu dùng",
            "Vay kinh doanh",
            "Vay sửa chữa nhà",
            "Vay du học",
            "Vay khác"
        ]
    )

    method = st.radio(
        "💳 Phương thức trả nợ",
        [
            "Dư nợ giảm dần - Gốc chia đều",
            "Trả đều hàng tháng - Niên kim"
        ]
    )

# =========================================================
# TÍNH TOÁN
# =========================================================

monthly_rate = interest_rate / 100 / 12

schedule = []

remaining = float(loan_amount)

# =========================================================
# PHƯƠNG PHÁP 1:
# DƯ NỢ GIẢM DẦN - GỐC CHIA ĐỀU
# =========================================================

if method == "Dư nợ giảm dần - Gốc chia đều":

    principal_monthly = loan_amount / loan_term

    for month in range(1, loan_term + 1):

        interest = remaining * monthly_rate

        payment = principal_monthly + interest

        new_remaining = max(
            0,
            remaining - principal_monthly
        )

        schedule.append({
            "Tháng": month,
            "Dư nợ đầu kỳ": remaining,
            "Gốc": principal_monthly,
            "Lãi": interest,
            "Tổng trả": payment,
            "Dư nợ cuối kỳ": new_remaining
        })

        remaining = new_remaining

# =========================================================
# PHƯƠNG PHÁP 2:
# TRẢ ĐỀU HÀNG THÁNG - NIÊN KIM
# =========================================================

else:

    if monthly_rate > 0:

        monthly_payment = (
            loan_amount
            * monthly_rate
            * (1 + monthly_rate) ** loan_term
            / (
                (1 + monthly_rate) ** loan_term - 1
            )
        )

    else:

        monthly_payment = loan_amount / loan_term

    for month in range(1, loan_term + 1):

        interest = remaining * monthly_rate

        principal = min(
            monthly_payment - interest,
            remaining
        )

        payment = principal + interest

        new_remaining = max(
            0,
            remaining - principal
        )

        schedule.append({
            "Tháng": month,
            "Dư nợ đầu kỳ": remaining,
            "Gốc": principal,
            "Lãi": interest,
            "Tổng trả": payment,
            "Dư nợ cuối kỳ": new_remaining
        })

        remaining = new_remaining


# =========================================================
# DATAFRAME
# =========================================================

df = pd.DataFrame(schedule)

# =========================================================
# TỔNG HỢP KHOẢN VAY
# =========================================================

total_interest = df["Lãi"].sum()

total_payment = df["Tổng trả"].sum()

first_month_payment = df.iloc[0]["Tổng trả"]

first_month_principal = df.iloc[0]["Gốc"]

first_month_interest = df.iloc[0]["Lãi"]

debt_ratio = (
    first_month_payment / income * 100
    if income > 0
    else 0
)

# =========================================================
# KẾT QUẢ CHÍNH
# =========================================================

st.header("📊 KẾT QUẢ KHOẢN VAY")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "💰 Tiền trả tháng đầu",
        format_money(first_month_payment)
    )

with m2:
    st.metric(
        "🏦 Tổng tiền lãi",
        format_money(total_interest)
    )

with m3:
    st.metric(
        "💵 Tổng tiền phải trả",
        format_money(total_payment)
    )

with m4:
    st.metric(
        "📉 Dư nợ cuối kỳ",
        format_money(df.iloc[-1]["Dư nợ cuối kỳ"])
    )

# =========================================================
# PHÂN TÍCH KHẢ NĂNG TRẢ NỢ
# =========================================================

st.subheader("📌 Đánh giá khả năng trả nợ")

if income <= 0:

    st.warning(
        "⚠️ Chưa nhập thu nhập hàng tháng nên "
        "chưa thể đánh giá khả năng trả nợ."
    )

elif debt_ratio <= 30:

    st.success(
        f"✅ Tỷ lệ trả nợ/thu nhập: {debt_ratio:.2f}% - "
        "Khả năng trả nợ tương đối tốt."
    )

elif debt_ratio <= 50:

    st.warning(
        f"⚠️ Tỷ lệ trả nợ/thu nhập: {debt_ratio:.2f}% - "
        "Cần cân nhắc khả năng tài chính."
    )

else:

    st.error(
        f"❌ Tỷ lệ trả nợ/thu nhập: {debt_ratio:.2f}% - "
        "Khoản trả nợ đang khá cao so với thu nhập."
    )


# =========================================================
# THÔNG TIN THÁNG ĐẦU
# =========================================================

st.subheader("📅 Chi tiết tháng đầu")

c1, c2, c3 = st.columns(3)

with c1:
    st.info(
        f"**Gốc tháng đầu**\n\n"
        f"{format_money(first_month_principal)}"
    )

with c2:
    st.info(
        f"**Lãi tháng đầu**\n\n"
        f"{format_money(first_month_interest)}"
    )

with c3:
    st.info(
        f"**Tổng trả tháng đầu**\n\n"
        f"{format_money(first_month_payment)}"
    )


# =========================================================
# BIỂU ĐỒ
# =========================================================

st.header("📈 BIỂU ĐỒ KHOẢN VAY")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    st.subheader("Gốc và lãi theo từng tháng")

    chart_data = df[
        ["Tháng", "Gốc", "Lãi"]
    ].set_index("Tháng")

    st.bar_chart(chart_data)


with chart_col2:

    st.subheader("Dư nợ còn lại")

    balance_data = df[
        ["Tháng", "Dư nợ cuối kỳ"]
    ].set_index("Tháng")

    st.line_chart(balance_data)


# =========================================================
# LỊCH TRẢ NỢ
# =========================================================

st.header("📋 LỊCH TRẢ NỢ CHI TIẾT")

display_df = df.copy()

for column in [
    "Dư nợ đầu kỳ",
    "Gốc",
    "Lãi",
    "Tổng trả",
    "Dư nợ cuối kỳ"
]:

    display_df[column] = display_df[column].apply(
        format_money
    )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# SO SÁNH 2 PHƯƠNG THỨC
# =========================================================

st.header("⚖️ SO SÁNH HAI PHƯƠNG THỨC TRẢ NỢ")


def calculate_equal_principal(
    amount,
    term,
    annual_rate
):

    rate = annual_rate / 100 / 12

    remaining_balance = float(amount)

    total_interest_method1 = 0
    first_payment_method1 = 0

    principal = amount / term

    for month in range(1, term + 1):

        interest = remaining_balance * rate

        payment = principal + interest

        total_interest_method1 += interest

        if month == 1:
            first_payment_method1 = payment

        remaining_balance -= principal

    return (
        first_payment_method1,
        total_interest_method1
    )


def calculate_annuity(
    amount,
    term,
    annual_rate
):

    rate = annual_rate / 100 / 12

    if rate > 0:

        payment = (
            amount
            * rate
            * (1 + rate) ** term
            / (
                (1 + rate) ** term - 1
            )
        )

    else:

        payment = amount / term

    remaining_balance = float(amount)

    total_interest_method2 = 0

    for month in range(term):

        interest = remaining_balance * rate

        principal = payment - interest

        remaining_balance -= principal

        total_interest_method2 += interest

    return (
        payment,
        total_interest_method2
    )


method1_first, method1_interest = calculate_equal_principal(
    loan_amount,
    loan_term,
    interest_rate
)

method2_first, method2_interest = calculate_annuity(
    loan_amount,
    loan_term,
    interest_rate
)

comparison_df = pd.DataFrame({
    "Tiêu chí": [
        "Tiền trả tháng đầu",
        "Tổng tiền lãi",
        "Tổng tiền phải trả"
    ],
    "Gốc chia đều": [
        method1_first,
        method1_interest,
        loan_amount + method1_interest
    ],
    "Niên kim": [
        method2_first,
        method2_interest,
        loan_amount + method2_interest
    ]
})

comparison_display = comparison_df.copy()

for column in [
    "Gốc chia đều",
    "Niên kim"
]:

    comparison_display[column] = comparison_display[column].apply(
        format_money
    )

st.dataframe(
    comparison_display,
    use_container_width=True,
    hide_index=True
)

if method1_interest < method2_interest:

    st.success(
        "💡 Với khoản vay hiện tại, phương thức "
        "**gốc chia đều** có tổng tiền lãi thấp hơn."
    )

elif method2_interest < method1_interest:

    st.success(
        "💡 Với khoản vay hiện tại, phương thức "
        "**niên kim** có tổng tiền lãi thấp hơn."
    )

else:

    st.info(
        "Hai phương thức có tổng tiền lãi bằng nhau "
        "với khoản vay hiện tại."
    )


# =========================================================
# TẢI FILE CSV
# =========================================================

st.header("📥 TẢI DỮ LIỆU")

csv_buffer = io.StringIO()

df.to_csv(
    csv_buffer,
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📊 Tải lịch trả nợ CSV",
    data=csv_buffer.getvalue(),
    file_name="lich_tra_no.csv",
    mime="text/csv"
)


# =========================================================
# PHIẾU THÔNG TIN KHOẢN VAY
# =========================================================

loan_info = f"""
========================================
       PHIẾU THÔNG TIN KHOẢN VAY
========================================

THÔNG TIN KHÁCH HÀNG
Họ và tên: {customer_name}
Số điện thoại: {phone}
CCCD: {cccd}
Thu nhập hàng tháng: {format_money(income)}

THÔNG TIN KHOẢN VAY
Số tiền vay: {format_money(loan_amount)}
Thời hạn vay: {loan_term} tháng
Lãi suất: {interest_rate}%/năm
Mục đích vay: {loan_purpose}
Phương thức trả nợ: {method}

KẾT QUẢ
Tiền gốc tháng đầu: {format_money(first_month_principal)}
Tiền lãi tháng đầu: {format_money(first_month_interest)}
Tổng trả tháng đầu: {format_money(first_month_payment)}

Tổng tiền lãi:
{format_money(total_interest)}

Tổng tiền phải trả:
{format_money(total_payment)}

Tỷ lệ trả nợ/thu nhập:
{debt_ratio:.2f}%

========================================
"""

st.download_button(
    label="📄 Tải phiếu thông tin khoản vay",
    data=loan_info,
    file_name="phieu_thong_tin_khoan_vay.txt",
    mime="text/plain"
)


# =========================================================
# CHATBOT GEMINI
# =========================================================

st.header("🤖 TRỢ LÝ AI TƯ VẤN KHOẢN VAY")

st.caption(
    "Bạn có thể hỏi AI về khoản vay đang tính, "
    "tiền trả hàng tháng, tổng lãi hoặc khả năng trả nợ."
)

# Kiểm tra API Key
api_key_available = False

try:

    if "GEMINI_API_KEY" in st.secrets:

        api_key_available = True

except Exception:

    api_key_available = False


if not api_key_available:

    st.warning(
        "⚠️ Chưa có GEMINI_API_KEY. "
        "Hãy thêm API key Gemini vào Streamlit Secrets."
    )

else:

    try:

        from google import genai

        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )

        # -------------------------------------------------
        # CÂU HỎI
        # -------------------------------------------------

        question = st.text_input(
            "💬 Nhập câu hỏi cho AI",
            placeholder=(
                "Ví dụ: Với khoản vay này, "
                "tháng đầu tôi phải trả bao nhiêu?"
            )
        )

        if question:

            system_prompt = f"""
Bạn là trợ lý AI tư vấn khoản vay ngân hàng.

Hãy trả lời bằng tiếng Việt, dễ hiểu, rõ ràng và ngắn gọn.

Bạn đang tư vấn dựa trên thông tin khoản vay hiện tại:

- Họ tên khách hàng: {customer_name}
- Số tiền vay: {format_money(loan_amount)}
- Thời hạn vay: {loan_term} tháng
- Lãi suất: {interest_rate}%/năm
- Mục đích vay: {loan_purpose}
- Phương thức trả nợ: {method}
- Thu nhập hàng tháng: {format_money(income)}
- Tiền gốc tháng đầu: {format_money(first_month_principal)}
- Tiền lãi tháng đầu: {format_money(first_month_interest)}
- Tổng trả tháng đầu: {format_money(first_month_payment)}
- Tổng tiền lãi: {format_money(total_interest)}
- Tổng tiền phải trả: {format_money(total_payment)}
- Tỷ lệ trả nợ/thu nhập: {debt_ratio:.2f}%

Lịch trả nợ:
{df.to_string(index=False)}

Nguyên tắc:
1. Nếu khách hỏi về số tiền hoặc lịch trả nợ, sử dụng số liệu ở trên.
2. Không tự ý thay đổi số liệu.
3. Nếu không đủ thông tin để trả lời, hãy nói rõ.
4. Đây là công cụ tham khảo, không phải quyết định phê duyệt khoản vay của ngân hàng.
5. Không cam kết khách hàng chắc chắn được ngân hàng duyệt vay.
"""

            user_prompt = f"""
{system_prompt}

Câu hỏi của khách hàng:

{question}
"""

            with st.spinner("🤖 Gemini đang trả lời..."):

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=user_prompt
                )

            st.success("🤖 Gemini trả lời:")

            st.markdown(response.text)

    except ImportError:

        st.error(
            "❌ Chưa cài thư viện Google GenAI."
        )

        st.code(
            "pip install -U google-genai"
        )

    except Exception as e:

        st.error(
            "❌ Không thể kết nối với Gemini API."
        )

        st.info(
            "Hãy kiểm tra GEMINI_API_KEY, "
            "tên model và giới hạn sử dụng API."
        )

        st.caption(
            f"Chi tiết lỗi: {str(e)}"
        )


# =========================================================
# NÚT RESET
# =========================================================

st.divider()

st.subheader("🔄 Làm mới ứng dụng")

if st.button("🔄 Tải lại / Xóa dữ liệu nhập"):

    st.rerun()


# =========================================================
# CHÂN TRANG
# =========================================================

st.divider()

st.caption(
    "🏦 Ứng dụng tính khoản vay ngân hàng | "
    "Hỗ trợ tính toán và tư vấn bằng Gemini AI"
)
