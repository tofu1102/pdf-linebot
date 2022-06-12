

def uploadFile(pdfPath):
    from pydrive.drive import GoogleDrive
    from pydrive.auth import GoogleAuth

    import os

    #Googleサービスを認証
    gauth = GoogleAuth()


    #資格情報ロードするか、存在しない場合は空の資格情報を作成
    gauth.LoadCredentialsFile("mycreds.txt")

    #Googleサービスの資格情報がない場合
    if gauth.credentials is None:
        #ユーザーから認証コードを自動的に受信しローカルWebサーバーを設定
        gauth.LocalWebserverAuth()
        #アクセストークンが存在しないか、期限切れかの場合
    elif gauth.access_token_expired:
        #Googleサービスを認証をリフレッシュする
        gauth.Refresh()
        #どちらにも一致しない場合
    else:
        #Googleサービスを承認する
        gauth.Authorize()
    #資格情報をtxt形式でファイルに保存する
    gauth.SaveCredentialsFile("mycreds.txt")

    #Googleドライブの認証処理
    drive = GoogleDrive(gauth)

    #アップロードするフォルダパス指定
    path = "static"

    #アップロード先の親フォルダのidを取得
    folder_id = drive.ListFile({'q': 'title = "sharable"'}).GetList()[0]['id']

    #GoogleDriveFileオブジェクト作成
    f = drive.CreateFile({'title' : pdfPath,"parents": [{"id": folder_id}]})
    #ローカルのファイルをセットしてアップロード
    f.SetContentFile(os.path.join(path,pdfPath))
    #Googleドライブにアップロード
    f.Upload()

    image_url = 'https://drive.google.com/uc?id=' + str( f['id'] )

    print(image_url)

    return image_url





if __name__=="__main__":
    uploadFile("static/計画書_B-2_B9TB2025_伊藤裕太.pdf")
