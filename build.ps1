$PACKAGE_NAME = "github"
$BUILD_DIR = [string]::IsNullOrEmpty($BUILD_DIR) ? ($PSScriptRoot + "\build") : $BUILD_DIR

if (!(Test-Path $BUILD_DIR)) {
  mkdir $BUILD_DIR
}

cd $PSScriptRoot

Compress-Archive `
  -Update `
  -Path src\*,LICENSE*,README* `
  -DestinationPath ($BUILD_DIR + "\" + $PACKAGE_NAME + ".keypirinha-package") 
