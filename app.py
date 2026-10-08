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

st.title("🏦 ỨNG DỤNG TÍNH KHOẢN VAY NGÂN HÀNG")
st.caption("Tính gốc - lãi hàng tháng và hỗ trợ tư vấn khoản vay bằng AI")

# =========================================================
# HÀM ĐỊNH DẠNG TIỀN
# =========================================================

def format_money(number):
    return f"{number:,.0f} VNĐ"


# =========================================================
# SIDEBAR - THÔNG TIN KHÁCH HÀNG
# =========================================================

st.sidebar.header("👤 Thông tin khách hàng")

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

st.header("💰 Thông tin khoản vay")

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
# TÍNH TOÁN KHOẢN VAY
# =========================================================

monthly_rate = interest_rate / 100 / 12

schedule = []

remaining = loan_amount

# ---------------------------------------------------------
# PHƯƠNG THỨC 1: DƯ NỢ GIẢM DẦN - GỐC CHIA ĐỀU
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# PHƯƠNG THỨC 2: TRẢ ĐỀU HÀNG THÁNG - NIÊN KIM
# ---------------------------------------------------------

else:

    if monthly_rate > 0:

        monthly_payment = (
            loan_amount
            * monthly_rate
            * (1 + monthly_rate) ** loan_term
            / ((1 + monthly_rate) ** loan_term - 1)
        )

    else:

        monthly_payment = loan_amount / loan_term

    for month in range(1, loan_term + 1):

        interest = remaining * monthly_rate

        principal = monthly_payment - interest

        principal = min(principal, remaining)

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

total_interest = df["Lãi"].sum()
total_payment = df["Tổng trả"].sum()

first_month_payment = df.iloc[0]["Tổng trả"]
first_month_principal = df.iloc[0]["Gốc"]
first_month_interest = df.iloc[0]["Lãi"]


# =========================================================
# KẾT QUẢ CHÍNH
# =========================================================

st.markdown("---")
st.header("📊 Kết quả khoản vay")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "💰 Số tiền vay",
        format_money(loan_amount)
    )

with c2:
    st.metric(
        "📅 Thời hạn",
        f"{loan_term} tháng"
    )

with c3:
    st.metric(
        "💸 Tổng tiền lãi",
        format_money(total_interest)
    )

with c4:
    st.metric(
        "💳 Tổng phải trả",
        format_money(total_payment)
    )


# =========================================================
# THÁNG ĐẦU TIÊN
# =========================================================

st.subheader("📌 Khoản phải trả tháng đầu")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Tổng trả tháng đầu",
        format_money(first_month_payment)
    )

with c2:
    st.metric(
        "Tiền gốc",
        format_money(first_month_principal)
    )

with c3:
    st.metric(
        "Tiền lãi",
        format_money(first_month_interest)
    )


# =========================================================
# ĐÁNH GIÁ KHẢ NĂNG TRẢ NỢ
# =========================================================

st.markdown("---")
st.header("📋 Đánh giá khả năng trả nợ")

if income > 0:

    debt_ratio = first_month_payment / income * 100

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Tỷ lệ trả nợ / thu nhập",
            f"{debt_ratio:.2f}%"
        )

    with col2:

        if debt_ratio <= 30:

            st.success(
                "✅ Khả năng trả nợ tương đối tốt."
            )

        elif debt_ratio <= 50:

            st.warning(
                "⚠️ Khoản trả nợ chiếm tỷ lệ khá cao."
            )

        else:

            st.error(
                "❌ Khoản trả nợ cao so với thu nhập."
            )

else:

    st.info(
        "Nhập thu nhập hàng tháng để đánh giá khả năng trả nợ."
    )


# =========================================================
# BIỂU ĐỒ GỐC VÀ LÃI
# =========================================================

st.markdown("---")
st.header("📈 Biểu đồ khoản vay")

chart_df = df[
    ["Tháng", "Gốc", "Lãi"]
].set_index("Tháng")

st.subheader("Gốc và lãi phải trả từng tháng")

st.bar_chart(chart_df)


# =========================================================
# BIỂU ĐỒ DƯ NỢ
# =========================================================

st.subheader("📉 Dư nợ còn lại")

balance_df = df[
    ["Tháng", "Dư nợ cuối kỳ"]
].set_index("Tháng")

st.line_chart(balance_df)


# =========================================================
# LỊCH TRẢ NỢ
# =========================================================

st.markdown("---")
st.header("📅 Lịch trả nợ chi tiết")

display_df = df.copy()

for column in [
    "Dư nợ đầu kỳ",
    "Gốc",
    "Lãi",
    "Tổng trả",
    "Dư nợ cuối kỳ"
]:

    display_df[column] = display_df[column].apply(
        lambda x: f"{x:,.0f} VNĐ"
    )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# SO SÁNH 2 PHƯƠNG THỨC
# =========================================================

st.markdown("---")
st.header("⚖️ So sánh phương thức trả nợ")


# Phương thức 1
remaining_1 = loan_amount
schedule_1 = []

principal_monthly_1 = loan_amount / loan_term

for month in range(1, loan_term + 1):

    interest_1 = remaining_1 * monthly_rate

    payment_1 = principal_monthly_1 + interest_1

    schedule_1.append({
        "Tháng": month,
        "Gốc": principal_monthly_1,
        "Lãi": interest_1,
        "Tổng trả": payment_1
    })

    remaining_1 = max(
        0,
        remaining_1 - principal_monthly_1
    )

df_1 = pd.DataFrame(schedule_1)

total_interest_1 = df_1["Lãi"].sum()
total_payment_1 = df_1["Tổng trả"].sum()


# Phương thức 2
remaining_2 = loan_amount
schedule_2 = []

if monthly_rate > 0:

    payment_2 = (
        loan_amount
        * monthly_rate
        * (1 + monthly_rate) ** loan_term
        / ((1 + monthly_rate) ** loan_term - 1)
    )

else:

    payment_2 = loan_amount / loan_term


for month in range(1, loan_term + 1):

    interest_2 = remaining_2 * monthly_rate

    principal_2 = payment_2 - interest_2

    principal_2 = min(
        principal_2,
        remaining_2
    )

    schedule_2.append({
        "Tháng": month,
        "Gốc": principal_2,
        "Lãi": interest_2,
        "Tổng trả": principal_2 + interest_2
    })

    remaining_2 = max(
        0,
        remaining_2 - principal_2
    )


df_2 = pd.DataFrame(schedule_2)

total_interest_2 = df_2["Lãi"].sum()
total_payment_2 = df_2["Tổng trả"].sum()


comparison_df = pd.DataFrame({
    "Phương thức": [
        "Dư nợ giảm dần - Gốc chia đều",
        "Trả đều hàng tháng - Niên kim"
    ],
    "Tổng tiền lãi": [
        total_interest_1,
        total_interest_2
    ],
    "Tổng tiền phải trả": [
        total_payment_1,
        total_payment_2
    ]
})


comparison_display = comparison_df.copy()

comparison_display["Tổng tiền lãi"] = (
    comparison_display["Tổng tiền lãi"]
    .apply(lambda x: f"{x:,.0f} VNĐ")
)

comparison_display["Tổng tiền phải trả"] = (
    comparison_display["Tổng tiền phải trả"]
    .apply(lambda x: f"{x:,.0f} VNĐ")
)

st.dataframe(
    comparison_display,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# XUẤT FILE CSV
# =========================================================

st.markdown("---")
st.header("📥 Xuất dữ liệu")

csv_buffer = io.StringIO()

df.to_csv(
    csv_buffer,
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 Tải lịch trả nợ CSV",
    data=csv_buffer.getvalue(),
    file_name="lich_tra_no.csv",
    mime="text/csv"
)


# =========================================================
# PHIẾU THÔNG TIN KHOẢN VAY
# =========================================================

loan_info = f"""
THÔNG TIN KHOẢN VAY
==============================

Khách hàng: {customer_name}
Số điện thoại: {phone}
CCCD: {cccd}

Số tiền vay: {loan_amount:,.0f} VNĐ
Thời hạn: {loan_term} tháng
Lãi suất: {interest_rate:.2f}%/năm
Mục đích vay: {loan_purpose}

Phương thức trả nợ:
{method}

Tháng đầu tiên:
- Tiền gốc: {first_month_principal:,.0f} VNĐ
- Tiền lãi: {first_month_interest:,.0f} VNĐ
- Tổng trả: {first_month_payment:,.0f} VNĐ

Tổng tiền lãi:
{total_interest:,.0f} VNĐ

Tổng tiền phải trả:
{total_payment:,.0f} VNĐ
"""

st.download_button(
    label="📄 Tải phiếu thông tin khoản vay",
    data=loan_info,
    file_name="thong_tin_khoan_vay.txt",
    mime="text/plain"
)


# =========================================================
# 🤖 CHATBOT AI - OPENAI API
# =========================================================

st.markdown("---")
st.header("🤖 Chatbot AI tư vấn khoản vay")

st.write(
    "Bạn có thể hỏi AI về khoản vay, tiền gốc, tiền lãi, "
    "thời hạn vay hoặc khả năng trả nợ."
)


# Kiểm tra API key
api_key_available = False

try:

    if "OPENAI_API_KEY" in st.secrets:

        api_key_available = True

except Exception:

    api_key_available = False


if not api_key_available:

    st.warning(
        "⚠️ Chưa có OPENAI_API_KEY. "
        "Hãy thêm API key vào .streamlit/secrets.toml "
        "hoặc phần Secrets của Streamlit Cloud."
    )

else:

    try:

        from openai import OpenAI

        client = OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"]
        )

        question = st.text_input(
            "💬 Nhập câu hỏi cho AI",
            placeholder=(
                "Ví dụ: Với khoản vay này, "
                "tháng đầu tôi phải trả bao nhiêu?"
            )
        )

        if question:

            with st.spinner("🤖 AI đang phân tích..."):

                context = f"""
Bạn là trợ lý AI của một ứng dụng tính khoản vay ngân hàng.

Hãy tư vấn bằng tiếng Việt, dễ hiểu và ngắn gọn.
Ưu tiên sử dụng chính xác các số liệu khoản vay được cung cấp dưới đây.

THÔNG TIN KHÁCH HÀNG:
- Họ tên: {customer_name if customer_name else "Chưa nhập"}
- Thu nhập hàng tháng: {income:,.0f} VNĐ

THÔNG TIN KHOẢN VAY:
- Số tiền vay: {loan_amount:,.0f} VNĐ
- Thời hạn: {loan_term} tháng
- Lãi suất: {interest_rate:.2f}%/năm
- Mục đích vay: {loan_purpose}
- Phương thức trả nợ: {method}

KẾT QUẢ TÍNH TOÁN:
- Gốc tháng đầu: {first_month_principal:,.0f} VNĐ
- Lãi tháng đầu: {first_month_interest:,.0f} VNĐ
- Tổng trả tháng đầu: {first_month_payment:,.0f} VNĐ
- Tổng tiền lãi: {total_interest:,.0f} VNĐ
- Tổng tiền phải trả: {total_payment:,.0f} VNĐ
- Tỷ lệ trả nợ / thu nhập: {debt_ratio:.2f}% nếu có thu nhập.

YÊU CẦU:
1. Trả lời đúng theo số liệu trên.
2. Nếu người dùng hỏi về tháng đầu tiên, hãy nêu tiền gốc,
   tiền lãi và tổng số tiền phải trả.
3. Nếu hỏi tổng chi phí, hãy nêu tổng tiền lãi và tổng tiền phải trả.
4. Nếu hỏi khả năng trả nợ, hãy giải thích dựa trên tỷ lệ
   trả nợ / thu nhập.
5. Không tự bịa chính sách của ngân hàng.
6. Không khẳng định khoản vay chắc chắn được ngân hàng duyệt.
7. Đây là công cụ tham khảo, không phải tư vấn tài chính chính thức.

CÂU HỎI CỦA KHÁCH HÀNG:
{question}
"""

                response = client.responses.create(
                    model="gpt-5-mini",
                    instructions=context,
                    input=question
                )

                answer = response.output_text

                st.success("🤖 AI trả lời:")
                st.write(answer)

    except ImportError:

        st.error(
            "❌ Chưa cài thư viện OpenAI. "
            "Hãy chạy: pip install openai"
        )

    except Exception as e:

        st.error(
            "❌ Không thể kết nối với OpenAI API."
        )

        st.caption(
            f"Chi tiết lỗi: {str(e)}"
        )


# =========================================================
# NÚT LÀM LẠI
# =========================================================

st.markdown("---")

if st.button("🔄 Nhập lại khoản vay"):

    st.rerun()
