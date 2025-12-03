' cscript .\budget_expense_processor.vbs




Dim objExcel, objWorkbook, objSheet, objCell
Set objExcel = CreateObject("Excel.Application")
objExcel.Visible = False

xlsxFileName = "2025_Budget_Expense.xlsx"
Set objWorkbook = objExcel.Workbooks.Open("C:\xampp\htdocs\acconuting-automation\budget_expense\" & xlsxFileName)

' ' Loop through all sheets
' For Each objSheet In objWorkbook.Sheets
'     WScript.Echo "Sheet: " & objSheet.Name
'     ' Loop through all used cells in the sheet
'     For Each objCell In objSheet.UsedRange
'         WScript.Echo "Row " & objCell.Row & ", Col " & objCell.Column & ": " & objCell.Value
'     Next
' Next

































Dim fso, filePath, textToAppend, file

Set fso = CreateObject("Scripting.FileSystemObject")
Set file = fso.OpenTextFile("budget_expense.sql", 8, True)






Function SafeValue1(cell)
    If IsNull(cell) Or Trim(cell) = "" Then
        SafeValue1 = 0
    Else
        ' Replace newline characters (vbCrLf, vbCr, vbLf) and double spaces with single space
        Dim cleanedValue
        cleanedValue = Replace(cell, vbCrLf, "")
        cleanedValue = Replace(cleanedValue, vbCr, "")
        cleanedValue = Replace(cleanedValue, vbLf, "")
        cleanedValue = Replace(cleanedValue, "  ", " ")
        cleanedValue = Replace(cleanedValue, "'", "`")
        cleanedValue = Replace(cleanedValue, "$", "")
        cleanedValue = Replace(cleanedValue, ",", "")
        SafeValue1 = Trim(cleanedValue)
    End If
End Function



Function SafeValue(cell)
    If IsNull(cell) Or Trim(cell) = "" Then
        SafeValue = 0
    Else
        ' Replace newline characters (vbCrLf, vbCr, vbLf) and double spaces with single space
        Dim cleanedValue
        cleanedValue = Replace(cell, vbCrLf, "")
        cleanedValue = Replace(cleanedValue, vbCr, "")
        cleanedValue = Replace(cleanedValue, vbLf, "")
        cleanedValue = Replace(cleanedValue, " ", "")
        cleanedValue = Replace(cleanedValue, "'", "`")
        cleanedValue = Replace(cleanedValue, "$", "")
        cleanedValue = Replace(cleanedValue, ",", "")
        SafeValue = Trim(cleanedValue)
    End If
End Function


' Create a mechanism to scann all tab that group up the rows start by column B with format "Actual YYYY" e.g. "Actual 2024" not case sensitive (Start by every column B appeared with "Actual YYYY" and end with the rest of the row before the next "Actual YYYY").

' Create RegExp object for "Actual YYYY"
Set regex = New RegExp
regex.IgnoreCase = True
regex.Pattern = "^Actual\s\d{4}$"

' Loop through all sheets
For Each objSheet In objWorkbook.Sheets
    WScript.Echo "Scanning Sheet: " & objSheet.Name
    
    lastRow = objSheet.UsedRange.Rows.Count
    currentGroup = ""
    giName = ""
    For i = 1 To lastRow
        cellValue = Trim(objSheet.Cells(i, 2).Value) ' Column B
        
        If regex.Test(cellValue) Then
            ' If we already have a group, output it before starting new
            If currentGroup <> "" Then
                WScript.Echo "Group Found from " & objSheet.Name & " :" & vbCrLf & currentGroup
                currentGroup = ""
            End If
            
            giName = objSheet.Cells(i, 1)
            ' Start new group and include this marker row
            currentGroup = "Start Group at Row " & i & " GI code: " & giName & vbCrLf
            currentGroup = currentGroup & Join(GetRowValues(objSheet, i), ", ") & vbCrLf
        Else
            If currentGroup <> "" Then
                ' Add current row to group
                currentGroup = currentGroup & Join(GetRowValues(objSheet, i), ", ") & vbCrLf
            End If
        End If
        stats = cellValue
        If giName <> "" And stats <> "" Then

            sqlstr = "REPLACE INTO `budget_expense` (FileName, Tab, GI_name, Statistics, January, February, March, April, May, June, July, August, September, October, November, December, Total) VALUES ('" & _
                SafeValue1(xlsxFileName) & "','" & SafeValue1(objSheet.Name) & "','" & SafeValue1(giName) & "','" & SafeValue1(stats) & "'," & _
                SafeValue(objSheet.Cells(i, 3)) & "," & SafeValue(objSheet.Cells(i, 4)) & "," & SafeValue(objSheet.Cells(i, 5)) & "," & SafeValue(objSheet.Cells(i, 6)) & "," & _
                SafeValue(objSheet.Cells(i, 7)) & "," & SafeValue(objSheet.Cells(i, 8)) & "," & SafeValue(objSheet.Cells(i, 9)) & "," & SafeValue(objSheet.Cells(i, 10)) & "," & _
                SafeValue(objSheet.Cells(i, 11)) & "," & SafeValue(objSheet.Cells(i, 12)) & "," & SafeValue(objSheet.Cells(i, 13)) & "," & SafeValue(objSheet.Cells(i, 14)) & "," & _
                SafeValue(objSheet.Cells(i, 15)) & ");"
            file.WriteLine sqlstr
            WScript.Echo sqlstr

        End If
    Next
    
    ' Output last group if exists
    If currentGroup <> "" Then
        WScript.Echo "Group Found:" & vbCrLf & currentGroup
    End If
Next

objWorkbook.Close False
objExcel.Quit
Set objWorkbook = Nothing
Set objExcel = Nothing


' Helper function to get all cell values in a row and replace commas
Function GetRowValues(sheet, rowIndex)
    Dim colCount, arr(), j, cellValue
    colCount = sheet.UsedRange.Columns.Count
    ReDim arr(colCount - 1)
    For j = 1 To colCount
        cellValue = sheet.Cells(rowIndex, j).Value
        If Not IsEmpty(cellValue) Then
            ' Replace all commas with empty string (or another character if needed)

            If IsNull(cellValue) Or Trim(CStr(cellValue) & "") = "" Then
                cellValue = ""
            Else
                cellValue = CStr(cellValue) ' Convert to string
                cellValue = Replace(cellValue, ",", "")
                cellValue = Replace(cellValue, "'", "`")
            End If

        End If
        arr(j - 1) = cellValue
    Next
    GetRowValues = arr
End Function









file.Close

Set file = Nothing
Set fso = Nothing























objWorkbook.Close False
objExcel.Quit
Set objWorkbook = Nothing
Set objExcel = Nothing
