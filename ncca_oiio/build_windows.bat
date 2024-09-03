@echo off
setlocal

REM Determine the script directory and cd to it
set SCRIPT_DIR=%~dp0
cd %SCRIPT_DIR%

set OIIO_DEPS_SOURCE_ROOT="%SCRIPT_DIR%\dependencies\src"
set OIIO_DEPS_INSTALL_ROOT="%SCRIPT_DIR%\dependencies\windows"

set ZLIB_ROOT=%OIIO_SOURCE_DEPS_ROOT%\zlib
cd %ZLIB_ROOT%
cmake -S . -B build -DCMAKE_INSTALL_PREFIX=%ZLIB_ROOT%
cmake --build build --config Release --target install
del build\Release\zlib.lib

set TIFF_ROOT=%OIIO_DEPS_SOURCE_ROOT%\libtiff
cd %TIFF_ROOT%
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DCMAKE_INSTALL_PREFIX=%OIIO_DEPS_INSTALL_ROOT%
cmake --build build --config Release --target install

set JPEG_ROOT=%OIIO_DEPS_SOURCE_ROOT%\libjpeg-turbo
cd %JPEG_ROOT%
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DENABLE_SHARED=OFF -DCMAKE_INSTALL_PREFIX=%OIIO_DEPS_INSTALL_ROOT%
cmake --build build --config Release --target install

set EXR_ROOT=%OIIO_DEPS_SOURCE_ROOT%\openexr
mkdir %EXR_ROOT%
cd %EXR_ROOT%
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=%OIIO_DEPS_INSTALL_ROOT% ^
  -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=OFF -DOPENEXR_BUILD_TOOLS=OFF ^
  -DOPENEXR_INSTALL_TOOLS=OFF -DOPENEXR_INSTALL_EXAMPLES=OFF ^
  -DZLIB_ROOT=%OIIO_DEPS_INSTALL_ROOT%
cmake --build build --target install --config Release

set OCIO_ROOT=%OIIO_DEPS_SOURCE_ROOT%\OpenColorIO
mkdir %OCIO_ROOT%
cd %OCIO_ROOT%
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=%OIIO_DEPS_INSTALL_ROOT% ^
    -DBUILD_SHARED_LIBS=YES ^
    -DOCIO_INSTALL_EXT_PACKAGES=ALL -DOCIO_BUILD_PYTHON=OFF

cmake --build build --target install --config Release

set OIIO_ROOT=%SCRIPT_DIR%/source
set OIIO_INSTALL_ROOT=%SCRIPT_DIR%/install/windows
cd %OIIO_ROOT%
cmake -S . -B build -DVERBOSE=ON -DCMAKE_BUILD_TYPE=Release ^
  -DZLIB_INCLUDE_DIR=%OIIO_DEPS_INSTALL_ROOT%/include ^
  -DZLIB_LIBRARY=%OIIO_DEPS_INSTALL_ROOT%/lib ^
  -DTIFF_ROOT=%OIIO_DEPS_INSTALL_ROOT% ^
  -DOpenEXR_ROOT=%OIIO_DEPS_INSTALL_ROOT% ^
  -DImath_DIR=%OIIO_DEPS_INSTALL_ROOT%\lib\cmake\Imath ^
  -DImath_INCLUDE_DIR=%OIIO_DEPS_INSTALL_ROOT%\include\Imath ^
  -DImath_LIBRARY=%OIIO_DEPS_INSTALL_ROOT%\lib\Imath-3_2.lib ^
  -DJPEG_ROOT=%OIIO_DEPS_INSTALL_ROOT% ^
  -Dlibjpeg-turbo_ROOT=%OIIO_DEPS_INSTALL_ROOT% ^
  -DOpenColorIO_ROOT=%OIIO_DEPS_INSTALL_ROOT% ^
  -DUSE_PYTHON=1 -DUSE_QT=0 -DBUILD_SHARED_LIBS=0 -DLINKSTATIC=1 ^
  -DCMAKE_INSTALL_PREFIX=%OIIO_INSTALL_ROOT% ^
  -DOpenImageIO_BUILD_MISSING_DEPS=all

echo OpenImageIO built and installed successfully in oiio_ncca.

endlocal
