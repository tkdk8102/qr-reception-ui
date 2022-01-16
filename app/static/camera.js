window.SQR = window.SQR || {}

SQR.reader = (() => {
    // QRコードから読み取ったデータをポストする先のURL指定
    const result_url = '/result'

    /**
     * getUserMedia()に非対応の場合は非対応の表示をする
     */
    const showUnsuportedScreen = () => {
        document.querySelector('#js-unsupported').classList.add('is-show')
    }
    if (!navigator.mediaDevices) {
        showUnsuportedScreen()
        return
    }

    const video = document.querySelector('#js-video')

    /**
     * videoの出力をCanvasに描画して画像化 jsQRを使用してQR解析
     */
    const checkQRUseLibrary = () => {
        const canvas = document.querySelector('#js-canvas')
        const ctx = canvas.getContext('2d')
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        const code = jsQR(imageData.data, canvas.width, canvas.height)

        if (code) {
            $.ajax({
                url: result_url,
                type: "POST",
                dataType: "json",
                data: {
                    gid: code.data
                }
            }).done(function(data) {
                // 通信成功時の処理
                SQR.modal.open(data) // モーダルを開き 4秒後に閉じる
                setTimeout(() => {
                    $('#result_modal').modal('hide');
                    SQR.reader.findQR() // QR解析を再開
                }, 4000)
            }).fail(function(data) {
                // 通信失敗時の処理
                $("#alert_audio")[0].play();
                alert('データベースの検索に失敗しました')
                window.location.reload(true)
            });
        } else {
            setTimeout(checkQRUseLibrary, 200)
        }
    }

    /**
     * videoの出力をBarcodeDetectorを使用してQR解析
     */
    const checkQRUseBarcodeDetector = () => {
        const barcodeDetector = new BarcodeDetector()
        barcodeDetector
            .detect(video)
            .then((barcodes) => {
                if (barcodes.length > 0) {
                    for (let barcode of barcodes) {
                        $.ajax({
                            url: result_url,
                            type: "POST",
                            dataType: "json",
                            data: {
                                gid: barcode.rawValue
                            }
                        }).done(function(data) {
                            // 通信成功時の処理
                            SQR.modal.open(data.kanji_name) // モーダルを開き 4秒後に閉じる
                            setTimeout(() => {
                                $('#result_modal').modal('hide');
                                SQR.reader.findQR() // QR解析を再開
                            }, 4000)
                        }).fail(function(data) {
                            // 通信失敗時の処理
                            $("#alert_audio")[0].play();
                            alert('データベースの検索に失敗しました')
                            window.location.reload(true)
                        });
                    }
                } else {
                    setTimeout(checkQRUseBarcodeDetector, 200)
                }
            })
            .catch(() => {
                console.error('Barcode Detection failed, boo.')
            })
    }

    /**
     * BarcodeDetector APIを使えるかどうかで処理を分岐
     */
    const findQR = () => {
        window.BarcodeDetector
            ? checkQRUseBarcodeDetector()
            : checkQRUseLibrary()
    }

    // インナー/アウターカメラの切り替え
    var front = true;
    if (getParam('camera') === 'rear') {
        front = !front;
    }

    // カメラオプション指定
    const options = {
        audio: false,
        video: { facingMode: (front? "user" : "environment"),
        }
    };
    if (front) {
        options.video["width"] = 1280
        options.video["height"] = 640
    }

    /**
     * デバイスのカメラを起動
     */
    const initCamera = () => {
        navigator.mediaDevices
            .getUserMedia(options)
            .then(function(mediaStream) {
                var video = document.querySelector('video');
                video.srcObject = mediaStream;
                video.onloadedmetadata = function(e) {
                    video.play();
                    findQR()
                };
            })
            .catch(() => {
                showUnsuportedScreen()
            })
    }

    return {
        initCamera,
        findQR,
    }
})()

// URL パラーメタ取得関数
function getParam(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

SQR.modal = (() => {
    var name = document.getElementById('name')
    var comment = document.getElementById('comment')

    /**
     * 取得した文字列を入れ込んでモーダルを開く
     */
    const open = (kanji_name) => {
        if (kanji_name) {
            $("#success_audio")[0].play();
            name.innerText = kanji_name + ' 様'
            comment.innerText = 'ご出席いただきありがとうございます'
        }else{
            $("#alert_audio")[0].play();
            name.innerText = '読み取りエラーです'
            comment.innerText = '受付にてご記帳をお願いいたします'
        }
        $('#result_modal').modal('show');
    }

    return {
        open,
    }
})()

if (SQR.reader) SQR.reader.initCamera()
