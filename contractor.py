import streamlit as st
import openai
from PyPDF2 import PdfReader

# Judul aplikasi
st.title("Asisten Analisis Kontrak dengan OpenAI")

# --- Bagian Sidebar untuk API Key ---
st.sidebar.header("Konfigurasi API")
api_key = st.sidebar.text_input("Masukkan OpenAI API Key", type="password")

# Mengatur API key jika diisi
if api_key:
    openai.api_key = api_key
else:
    st.warning("Silakan masukkan OpenAI API Key Anda di sidebar untuk melanjutkan.")

# --- Fungsi untuk mengekstrak teks dari PDF ---
def extract_text_from_pdf(file):
    """Mengekstrak teks dari file PDF yang diunggah."""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file PDF: {e}")
        return None

# --- Fungsi untuk memanggil API OpenAI ---
def get_openai_response(prompt, text_data):
    """Mengirimkan teks dan prompt ke API OpenAI dan mengembalikan respons."""
    try:
        if not openai.api_key:
            st.error("OpenAI API Key belum diatur.")
            return "Error: OpenAI API Key belum diatur."

        # Gabungkan prompt dengan teks dokumen
        full_prompt = f"{prompt}\n\nBerikut adalah teks kontraknya:\n\n{text_data}"

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Anda bisa mengganti dengan model lain seperti "gpt-4"
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except openai.RateLimitError:
        return "Anda telah mencapai batas penggunaan API. Mohon coba lagi nanti atau periksa paket langganan Anda."
    except openai.AuthenticationError:
        return "Autentikasi API gagal. Pastikan API key yang Anda masukkan benar dan valid."
    except Exception as e:
        return f"Terjadi kesalahan: {e}"

# --- Bagian Utama Aplikasi ---
uploaded_file = st.file_uploader("Unggah dokumen kontrak (PDF)", type=["pdf"])

if uploaded_file is not None and openai.api_key:
    # Memuat spinner saat memproses file
    with st.spinner("Mengekstrak teks dari PDF..."):
        contract_text = extract_text_from_pdf(uploaded_file)
    
    if contract_text:
        st.success("Teks berhasil diekstrak!")
        
        # Opsi analisis
        st.header("Pilih Analisis yang Diinginkan")
        analysis_options = {
            "Ringkasan": "Buatkan ringkasan dari dokumen kontrak ini.",
            "Poin Penting": "Identifikasi poin-poin penting, klausul, dan ketentuan utama dalam dokumen ini.",
            "Risiko Potensial": "Analisis risiko potensial dan masalah hukum yang mungkin ada dalam kontrak ini.",
            "Tanyakan Sesuai Kebutuhan": "Tuliskan pertanyaan spesifik Anda:"
        }
        
        selected_analysis = st.selectbox(
            "Pilih jenis analisis:",
            list(analysis_options.keys())
        )
        
        if selected_analysis == "Tanyakan Sesuai Kebutuhan":
            user_prompt = st.text_area("Masukkan pertanyaan Anda:")
            if st.button("Analisis"):
                if user_prompt:
                    with st.spinner("Menganalisis dokumen dengan OpenAI..."):
                        response = get_openai_response(user_prompt, contract_text)
                        st.subheader("Hasil Analisis")
                        st.write(response)
                else:
                    st.warning("Mohon masukkan pertanyaan Anda.")
        else:
            prompt_template = analysis_options[selected_analysis]
            if st.button("Analisis"):
                with st.spinner("Menganalisis dokumen dengan OpenAI..."):
                    response = get_openai_response(prompt_template, contract_text)
                    st.subheader("Hasil Analisis")
                    st.write(response)
