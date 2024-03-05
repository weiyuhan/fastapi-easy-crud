import setuptools

setuptools.setup(
    name="ydwh_fastapi_shared",  # Replace with your username
    version="0.0.1",
    author="Yuhan Wei",
    author_email="weiyuhan@pku.edu.cn",
    description="Share python utils for Youdianwenhua",
    url="https://github.com/Youdianwenhua2023/shared",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        'uvicorn==0.21.1',
        'fastapi==0.95.1',
        'python-dotenv==1.0.0',
        'pytest==7.3.1',
        'black==23.3.0',
        'mypy==1.2.0',
        'isort==5.12.0',
        'httpx==0.24.0',
        'pymysql==1.0.3',
        'autoflake==2.1.1',
        'flake8==6.0.0',
        'pytest-cov==4.0.0',
        'loguru==0.7.0'
    ]
)
