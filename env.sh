
module load cray-python
module load PrgEnv-gnu
module load cray-hdf5-parallel
module load cray-netcdf-hdf5parallel

export IO_BENCHMARKS_ROOT=${HOME/home/work}/.io_benchmarks
mkdir -p $IO_BENCHMARKS_ROOT
if [ ! -d  "$IO_BENCHMARKS_ROOT/io_env" ]; then
    python3 -m venv "$IO_BENCHMARKS_ROOT/io_env"
    source "$IO_BENCHMARKS_ROOT/io_env/bin/activate"
    python3 -m pip install pip --upgrade
fi


 