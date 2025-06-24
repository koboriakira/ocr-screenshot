-- ページ数
set pages to 226
-- 対象アプリ
set target to "Kindle"
-- 保存フォルダ
set savepath to "/Users/a_kobori/Documents/KindleOCR/ゲーム理論の裏口入門_ボードゲームで学ぶ戦略的思考法/"
-- 開始ファイル番号
set spage to 1
-- めくり方向(1=左 2=右)
set pagedir to 1
-- ページめくりウエイト(秒)
set pausetime to 1.0
-- 切り抜きサイズ(中心から)
set cropx to 0
set cropy to 0
-- リサイズ横
set resizew to 0

if pagedir = 1 then
	set keychar to (ASCII character 28)
else
	set keychar to (ASCII character 29)
end if

if target is not "" then
	tell application target
		activate
	end tell
end if

delay pausetime

repeat with i from spage to pages
	-- 3ケタゼロパディング処理
	set numText to i as string
	if i < 10 then
		set dp to "00" & numText
	else if i < 100 then
		set dp to "0" & numText
	else
		set dp to numText
	end if
	
	set spath to (savepath & "p" & dp & ".png")
	
	do shell script "screencapture " & quoted form of spath
	
	if cropx is not 0 and cropy is not 0 then
		if resizew is not 0 then
			do shell script "sips -c " & cropy & " " & cropx & " --resampleWidth " & resizew & " " & quoted form of spath & " --out " & quoted form of spath
		else
			do shell script "sips -c " & cropy & " " & cropx & " " & quoted form of spath & " --out " & quoted form of spath
		end if
	end if
	
	tell application "System Events"
		keystroke keychar
	end tell
	
	delay pausetime
end repeat

activate
