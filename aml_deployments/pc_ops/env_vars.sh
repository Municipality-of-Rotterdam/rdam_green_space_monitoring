# Make sure to install CloudComPy in your image (Not included in Dockerfile), and point to that location
# export CLOUDCOMPY_ROOT=LOCATION_OF_CloudComPy310 (e.g. path/to/CloudComPy310)

# Set up CloudComPy environment variables and echo the values being set
export CLOUDCOMPY_ROOT=$CLOUDCOMPY_ROOT
export CONDA_ENV_ROOT=\$(realpath "\$(dirname \$(which python))/..")
export LD_LIBRARY_PATH=\${CONDA_ENV_ROOT}/lib:\${LD_LIBRARY_PATH}
export PATH=\${CLOUDCOMPY_ROOT}/bin:\${PATH}
export PYTHONPATH=\${CLOUDCOMPY_ROOT}/lib/cloudcompare:\${PYTHONPATH}
export PYTHONPATH=\${CLOUDCOMPY_ROOT}/doc/PythonAPI_test:\${PYTHONPATH}
export LD_LIBRARY_PATH=\${CLOUDCOMPY_ROOT}/lib/cloudcompare:\${CLOUDCOMPY_ROOT}/lib/cloudcompare/plugins:\${LD_LIBRARY_PATH}
export QT_QPA_PLATFORM=offscreen
echo "CONDA_ENV_ROOT: $CONDA_ENV_ROOT"
echo "PYTHONPATH: $PYTHONPATH"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
echo "QT_QPA_PLATFORM: $QT_QPA_PLATFORM"
