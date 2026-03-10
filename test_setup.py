print('Testing all imports...')
all_ok = True
packages = {
    'openai': 'openai',
    'langchain': 'langchain',
    'faiss': 'faiss-cpu',
    'sentence_transformers': 'sentence-transformers',
    'fitz': 'PyMuPDF',
    'pdfplumber': 'pdfplumber',
    'docx': 'python-docx',
    'pandas': 'pandas',
    'sqlalchemy': 'sqlalchemy',
    'streamlit': 'streamlit',
    'plotly': 'plotly',
    'reportlab': 'reportlab',
    'googleapiclient': 'google-api-python-client',
    'apscheduler': 'APScheduler',
}
for module, package in packages.items():
    try:
        __import__(module)
        print(f'  OK {package}')
    except ImportError:
        print(f'  MISSING: {package}')
        all_ok = False

print()
if all_ok:
    print('All packages installed! Ready to build.')
else:
    print('Some packages missing. Run: pip install -r requirements.txt')
