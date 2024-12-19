# smartiq-src


## Build
1. Remove old build from the dist folder
```bash
Remove-Item -Path .\dist\* -Recurse
```
2. build the project by poetry
```bash
poetry build 
```
3. build docker image
```bash
docker buildx build --progress=plain -t lisa-srm:3.11-slim .
```
4. 
```bash
docker run --name lisa-srm lisa-srm:3.11-slim
docker run -d --name lisa-srm lisa-srm:3.11-slim
```