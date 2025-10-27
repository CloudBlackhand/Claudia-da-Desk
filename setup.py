from setuptools import setup, find_packages

setup(
    name="claudia-da-desk",
    version="1.0.0",
    description="Sistema de Cobrança WhatsApp com IA",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "Flask-CORS==4.0.0",
        "psycopg2-binary==2.9.7",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "gunicorn==21.2.0",
    ],
    python_requires=">=3.8",
)
