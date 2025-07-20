-- 保存先ディレクトリ（共通部分とサブディレクトリに分割）
property DEFAULT_SUBDIR : "みんなが欲しかった！FPの教科書3級 2025-2026年版"
property DEFAULT_BASEDIR : "/Users/koboriakira/Documents/KindleOCR"

-- めくり方向
property PAGE_LEFT : 1
property PAGE_RIGHT : 2
set pagedir to PAGE_RIGHT

-- ページ数（とりあえず最後まで読み取るぐらいの値を設定）
property DEFAULT_PAGES : 500

-- 以降は変更不要

property DEFAULT_SAVEPATH : DEFAULT_BASEDIR & "/" & DEFAULT_SUBDIR & "/"

set pages to DEFAULT_PAGES
set target to "Kindle"
set savepath to DEFAULT_SAVEPATH
-- 保存先ディレクトリが存在しない場合は作成
do shell script "mkdir -p " & quoted form of savepath
set spage to 1
set pausetime to 1.0
set cropx to 0
set cropy to 0
set resizew to 0

if pagedir = PAGE_LEFT then
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
