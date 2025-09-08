@echo off
echo Installing PDF conversion dependencies using miniforge...
echo.

REM Activate miniforge environment
call conda activate base

REM Install required packages
echo Installing WeasyPrint and dependencies...
conda install -c conda-forge weasyprint markdown pygments -y

REM Install additional dependencies that might be needed
echo Installing additional dependencies...
conda install -c conda-forge cffi pango -y

echo.
echo Installation complete!
echo You can now run: python convert_paper_to_pdf.py
echo.
pause
