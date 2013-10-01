import os
from setuptools import setup


# Utility function to pass text files content as setup() parameters.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="openerp_jsonrpc_client",
    version='0.1.a',
    author="Cyril MORISSE",
    author_email="cmorisse@boxes3.net",
    description=("A library to make RPC on an OpenERP Server using the JSON-RPC protocol."),
    license=read('LICENCE.txt'),
    keywords='openerp rpc jsonrpc client',
    url="http://bitbucket.org/cmorisse/openerp-jsonrpc-client",
    packages=['openerp_jsonrpc_client'],
    long_description=read('README.txt'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP'
    ],
    install_requires = ['requests==1.1.0', ],
)
