CONDA_ENV_ROOT=$(realpath "$(dirname "$(which python)")/..") 
SITE_PACKAGES=$(python -c "import site; print([p for p in site.getsitepackages() if 'site-packages' in p][0])") 
export PYTHONPATH="${SITE_PACKAGES}/cloudcompy/lib/cloudcompare:/anaconda/bin/python"
export LD_LIBRARY_PATH="${SITE_PACKAGES}/cloudcompy/lib/cloudcompare:${SITE_PACKAGES}/cloudcompy/lib/cloudcompare/plugins:${CONDA_ENV_ROOT}/lib:/usr/local/lib"
export QT_QPA_PLATFORM=offscreen
echo "CONDA_ENV_ROOT: $CONDA_ENV_ROOT"
echo "SITE_PACKAGES: $SITE_PACKAGES"
echo "PYTHONPATH: $PYTHONPATH"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
echo "QT_QPA_PLATFORM: $QT_QPA_PLATFORM"
