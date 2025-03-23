<<<<<<< HEAD
print("Hello Mars")

log_file = "mission_computer_main.log"
report_file = "log_analysis.md"

try:
    with open(log_file, "r", encoding="utf-8") as file:
        log_data = file.readlines() 
    
    log_data.reverse() 

    print(f"'{log_file}' 파일 내용 출력:")
    for line in log_data:
        print(line.strip()) 

    error_logs = [line.strip() for line in log_data if "Oxygen" in line]

    print("오류 로그 출력:\n")
    for log in error_logs:
        print(log)

    with open(report_file, "w", encoding="utf-8") as report:
        report.write("# 로그 분석 보고서\n")
        report.write(f"### 총 오류 로그 개수: {len(error_logs)}개\n")
        report.write("### 오류 로그\n")
        if error_logs:
            for log in error_logs:
                report.write(f"- {log}\n")
        else:
            report.write("### 오류 로그 없음\n")

    print("분석 저장 완료")

except FileNotFoundError:
    print(f"파일 '{log_file}'을 찾을 수 없습니다")
except Exception as e:
    print(f"오류 발생: {e}")
=======
print("Hello Mars")

log_file = "mission_computer_main.log"
report_file = "log_analysis.md"

try:
    with open(log_file, "r", encoding="utf-8") as file:
        log_data = file.readlines() 
    
    log_data.reverse() 

    print(f"'{log_file}' 파일 내용 출력:")
    for line in log_data:
        print(line.strip()) 

    error_logs = [line.strip() for line in log_data if "Oxygen" in line]

    print("오류 로그 출력:\n")
    for log in error_logs:
        print(log)

    with open(report_file, "w", encoding="utf-8") as report:
        report.write("# 로그 분석 보고서\n")
        report.write(f"### 총 오류 로그 개수: {len(error_logs)}개\n")
        report.write("### 오류 로그\n")
        if error_logs:
            for log in error_logs:
                report.write(f"- {log}\n")
        else:
            report.write("### 오류 로그 없음\n")

    print("분석 저장 완료")

except FileNotFoundError:
    print(f"파일 '{log_file}'을 찾을 수 없습니다")
except Exception as e:
    print(f"오류 발생: {e}")
>>>>>>> a326963 (Initial commit)
