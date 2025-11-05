# DjangoAuth
建置 Docker 映像檔的指令
docker-compose build

啟動服務
docker-compose up -d

列出您本地的 Docker 映像檔
docker images

將 Docker 映像檔儲存為 tar 檔案。
docker save -o djangoauth_web.tar djangoauth-web:latest

將剛剛生成的 django-auth-app.tar 檔案複製到您的群暉 NAS 上的任意共用資料夾中
透過群暉 DSM 的檔案總管直接上傳
在群暉NAS
點選File Station >> 選擇 docker目錄 >> 上傳 >> 上傳-覆寫 >> 找尋djangoauth_web.tar >> 開啟

步驟 3：在群暉 Docker 應用程式中匯入映像
登入您的群暉 DSM。
打開 「Docker」 應用程式。
在左側面板中，點擊 「映像」。
點擊 「新增」 按鈕，然後選擇 「從檔案新增」。
在彈出的視窗中，點擊 「瀏覽」，然後找到並選擇您剛剛上傳到 NAS 的 django-auth-app.tar 檔案。
點擊 「下一步」 或 「應用」，Docker 應用程式會開始匯入映像。這可能需要一些時間。