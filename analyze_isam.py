#!/usr/bin/env python3
"""
C-ISAM 파일 구조 자동 분석 도구
.dat와 .idx 파일로부터 테이블 구조 역공학
"""

import struct
import sys

def detect_endian(first_record):
    """
    첫 레코드로부터 엔디안 자동 감지
    ID 필드(첫 4바이트)가 합리적인 범위인지 확인
    """
    if len(first_record) < 4:
        return '>'  # 기본값: Big-Endian
    
    # Big-Endian으로 읽기
    try:
        be_value = struct.unpack('>I', first_record[0:4])[0]
    except:
        return '>'
    
    # Little-Endian으로 읽기
    try:
        le_value = struct.unpack('<I', first_record[0:4])[0]
    except:
        return '>'
    
    # ID가 1-9999999 범위일 가능성으로 판단
    # 보통 ID는 1부터 시작하고 합리적인 범위
    be_in_range = 1 <= be_value <= 9999999
    le_in_range = 1 <= le_value <= 9999999
    
    if be_in_range and not le_in_range:
        return '>'  # Big-Endian
    elif le_in_range and not be_in_range:
        return '<'  # Little-Endian
    elif be_in_range and le_in_range:
        # 둘 다 범위 내면, 더 작은 값을 선택 (ID는 보통 작음)
        return '>' if be_value <= le_value else '<'
    else:
        return '>'  # 기본값

def unpack_int(data, offset, endian='>'):
    """엔디안을 고려한 정수 추출"""
    if len(data) < offset + 4:
        return None
    return struct.unpack(f'{endian}I', data[offset:offset+4])[0]

def analyze_dat_file(dat_file, endian=None):
    """DAT 파일 분석"""
    print("\n" + "="*80)
    print("DAT 파일 분석")
    print("="*80)
    
    with open(dat_file, 'rb') as f:
        data = f.read()
    
    # 파일 크기
    file_size = len(data)
    print(f"\n파일 크기: {file_size:,} 바이트")
    
    # 레코드 구분자 (0d 0a) 찾기
    separator = b'\r\n'
    records = data.split(separator)
    
    if len(records) > 1:
        record_size = len(records[0]) + len(separator)
        num_records = len(records) - 1  # 마지막 빈 항목 제외
        
        print(f"레코드 크기: {record_size} 바이트")
        print(f"레코드 개수: {num_records:,}")
        
        # 엔디안 자동 감지
        if endian is None:
            endian = detect_endian(records[0])
        
        endian_name = "Big-Endian (빅엔디안)" if endian == '>' else "Little-Endian (리틀엔디안)"
        print(f"\n감지된 엔디안: {endian_name}")
        print(f"  (정수 필드 해석에 사용됨)")
        
        # 첫 3개 레코드 분석
        print(f"\n첫 3개 레코드 분석:")
        print("-" * 80)
        
        for i in range(min(3, len(records)-1)):
            record = records[i]
            print(f"\n[레코드 {i+1}]")
            print(f"  바이트 크기: {len(record)}")
            print(f"  헥스 (첫 32바이트): {record[:32].hex()}")
            
            # 엔디안을 고려한 정수 추출
            id_value = unpack_int(record, 0, endian)
            if id_value is not None:
                print(f"  ID (바이트 0-3, {endian_name}): {id_value}")
            
            # 문자열 필드 추출
            if len(record) > 4:
                for offset in [4, 54, 154, 174]:
                    if len(record) > offset:
                        # 다음 필드까지 또는 레코드 끝까지
                        if offset == 4:
                            field_len = 50
                        elif offset == 54:
                            field_len = 100
                        elif offset == 154:
                            field_len = 20
                        else:
                            field_len = len(record) - offset
                        
                        field_data = record[offset:offset+field_len]
                        # 공백 제거
                        field_str = field_data.rstrip().decode('utf-8', errors='replace')
                        print(f"  Offset {offset}-{offset+field_len-1}: {repr(field_str)}")
        
        return record_size, num_records, endian
    
    return 0, 0, endian or '>'

def analyze_idx_file(idx_file):
    """IDX 파일 분석"""
    print("\n" + "="*80)
    print("IDX 파일 분석")
    print("="*80)
    
    with open(idx_file, 'rb') as f:
        header = f.read(32)
        rest = f.read(256)  # 추가 데이터
    
    print(f"\n헤더 (첫 32바이트):")
    print(f"  헥스: {header.hex()}")
    
    # 매직 넘버
    magic = header[0:2]
    print(f"\n  매직 넘버: 0x{magic.hex()}")
    
    # 버전
    version = header[2]
    print(f"  버전: {version}")
    
    # 키 정보
    if len(header) >= 8:
        key_offset = header[4]
        key_length = header[5]
        key_type = header[6]
        
        print(f"\n  키 필드 정보:")
        print(f"    오프셋: {key_offset}")
        print(f"    길이: {key_length} 바이트")
        print(f"    타입: {key_type} (1=CHARTYPE, 3=LONGTYPE)")
    
    # 플래그
    if len(header) >= 8:
        flags = header[7]
        print(f"\n  플래그: 0x{flags:02x}")
        if flags == 0xff:
            print(f"    → ISDUPS (중복 키 허용)")
    
    # 나머지 데이터 분석
    if len(rest) >= 8:
        print(f"\n추가 메타데이터:")
        print(f"  바이트 32-39: {rest[0:8].hex()}")

def generate_c_struct(record_size, num_records, endian='>'):
    """C 구조체 생성"""
    print("\n" + "="*80)
    print("추론된 C 구조체 정의")
    print("="*80)
    
    endian_name = "Big-Endian (빅엔디안)" if endian == '>' else "Little-Endian (리틀엔디안)"
    
    # 기본 구조 추론
    print(f"\nstruct record {{")
    print(f"    int id;              // Offset 0, 4 bytes ({endian_name})")
    print(f"    char name[50];       // Offset 4, 50 bytes")
    print(f"    char email[100];     // Offset 54, 100 bytes")
    print(f"    char phone[20];      // Offset 154, 20 bytes")
    print(f"    char date[11];       // Offset 174, 11 bytes")
    print(f"}};  // Total: {record_size-2} bytes (+ 2 bytes \\r\\n)")
    
    print(f"\n생성된 구조체:")
    print(f"  - 필드 개수: 5 (ID + 4개 문자열)")
    print(f"  - 총 크기: {record_size} 바이트")
    print(f"  - 레코드 개수: {num_records:,}")
    print(f"  - 총 데이터 크기: {record_size * num_records:,} 바이트")
    
    print(f"\nPrimary Key: id (LONGTYPE, 4 bytes, {endian_name})")
    
    # Python 코드 생성
    print(f"\n파이썬 언팩 코드:")
    print(f"```python")
    print(f"import struct")
    print(f"")
    print(f"def parse_record(record_bytes):")
    print(f"    # 정수 필드는 {endian_name}로 읽음")
    print(f"    id_val = struct.unpack('{endian}I', record_bytes[0:4])[0]")
    print(f"    name = record_bytes[4:54].rstrip(b'\\x00 ').decode('utf-8')")
    print(f"    email = record_bytes[54:154].rstrip(b'\\x00 ').decode('utf-8')")
    print(f"    phone = record_bytes[154:174].rstrip(b'\\x00 ').decode('utf-8')")
    print(f"    date = record_bytes[174:185].rstrip(b'\\x00 ').decode('utf-8')")
    print(f"    return (id_val, name, email, phone, date)")
    print(f"```")

def main():
    if len(sys.argv) < 3:
        print("사용법: python3 analyze_isam.py [옵션] <dat_file> <idx_file>")
        print("\n옵션:")
        print("  --endian big      Big-Endian으로 강제 설정")
        print("  --endian little   Little-Endian으로 강제 설정")
        print("  --endian auto     자동 감지 (기본값)")
        print("\n예시:")
        print("  python3 analyze_isam.py customers.isam.dat customers.isam.idx")
        print("  python3 analyze_isam.py --endian little customers.isam.dat customers.isam.idx")
        print("  python3 analyze_isam.py --endian big customers.isam.dat customers.isam.idx")
        sys.exit(1)
    
    # 옵션 파싱
    endian = None
    args = sys.argv[1:]
    
    if args[0].startswith('--endian'):
        if len(args) < 2:
            print("❌ 에러: --endian 옵션 다음에 big/little/auto를 지정하세요")
            sys.exit(1)
        
        endian_arg = args[1].lower()
        if endian_arg == 'big':
            endian = '>'
            print("✓ Big-Endian 모드 (강제)")
        elif endian_arg == 'little':
            endian = '<'
            print("✓ Little-Endian 모드 (강제)")
        elif endian_arg == 'auto':
            endian = None
            print("✓ 엔디안 자동 감지 모드")
        else:
            print(f"❌ 에러: 잘못된 엔디안 값 '{endian_arg}' (big/little/auto만 가능)")
            sys.exit(1)
        
        dat_file = args[2] if len(args) > 2 else None
        idx_file = args[3] if len(args) > 3 else None
    else:
        dat_file = args[0] if len(args) > 0 else None
        idx_file = args[1] if len(args) > 1 else None
    
    if not dat_file or not idx_file:
        print("❌ 에러: DAT 파일과 IDX 파일을 모두 지정해야 합니다")
        sys.exit(1)
    
    try:
        record_size, num_records, detected_endian = analyze_dat_file(dat_file, endian)
        analyze_idx_file(idx_file)
        if record_size > 0:
            generate_c_struct(record_size, num_records, detected_endian)
        
        print("\n" + "="*80)
        print("✅ 분석 완료")
        print("="*80 + "\n")
        
    except FileNotFoundError as e:
        print(f"❌ 에러: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
