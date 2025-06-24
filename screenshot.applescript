-- �y�[�W��
set pages to 226
-- �ΏۃA�v��
set target to "Kindle"
-- �ۑ��t�H���_
set savepath to "/Users/a_kobori/Documents/KindleOCR/�Q�[�����_�̗�������_�{�[�h�Q�[���Ŋw�Ԑ헪�I�v�l�@/"
-- �J�n�t�@�C���ԍ�
set spage to 1
-- �߂������(1=�� 2=�E)
set pagedir to 1
-- �y�[�W�߂���E�G�C�g(�b)
set pausetime to 1.0
-- �؂蔲���T�C�Y(���S����)
set cropx to 0
set cropy to 0
-- ���T�C�Y��
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
	-- 3�P�^�[���p�f�B���O����
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
