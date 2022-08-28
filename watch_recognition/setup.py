import setuptools

setuptools.setup(
    name="watch_recognition",
    version="0.0.1",
    author="Artur Kucia",
    author_email="author@example.com",
    description="Reading time from analog clocks",
    long_description_content_type="",
    url="https://github.com/akucia/analog-watch-recognition",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "tensorflow~=2.9.1",
        "tensorflow-serving-api~=2.9.1",
        "keras-cv==0.2.10",
        "pandas>=1.0.0",
        "albumentations~=1.0.3",
        "tqdm~=4.62.1",
        "matplotlib~=3.4.3",
        "scikit-image~=0.18.2",
        "Pillow~=9.0.1",
        "scikit-learn~=0.24.1",
        "pycocotools==2.0.4",
        "click",
        "requests",
        "segmentation_models",
        "distinctipy==1.1.5",
        "google-cloud-storage>=2.5.0",
        "google-api-python-client>=2.58.0",
        "more-itertools~=8.14.0",
    ],
)
