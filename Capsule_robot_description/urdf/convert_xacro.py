import os
import re

def convert_xacro_to_urdf(xacro_filename, urdf_filename):
    """
    .xacro 파일을 읽어서 PyBullet용 .urdf 파일로 변환합니다.
    1. xacro 관련 태그 삭제
    2. package:// 경로를 절대 경로로 수정
    """
    
    # 현재 스크립트가 있는 폴더 (urdf 폴더)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 프로젝트 루트 폴더 (Capsule_robot_description 폴더) 찾기
    # (urdf 폴더의 부모 폴더)
    project_root = os.path.dirname(current_dir)
    
    # 입력 파일 경로
    input_path = os.path.join(current_dir, xacro_filename)
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"--- '{xacro_filename}' 파일 읽기 성공 ---")
        
        # 1. Xacro 헤더 및 include 태그 삭제
        # <xacro:include ... /> 줄을 모두 찾아서 삭제
        content = re.sub(r'<xacro:include.*?>', '', content)
        
        # <robot ... xmlns:xacro="..."> 에서 xacro 속성 삭제 (선택사항이지만 깔끔하게)
        content = re.sub(r'\sxmlns:xacro=".*?"', '', content)
        
        # 2. 파일 경로 수정 (핵심!)
        # package://Capsule_robot_description/meshes/...  ->  /home/shinwoo/.../meshes/...
        # (package://패키지명/ 부분을 프로젝트 루트 절대 경로로 치환)
        
        # 정규식으로 'package://어떤폴더명/' 패턴을 찾습니다.
        # 그리고 그것을 project_root + "/" 로 바꿉니다.
        
        def replace_package_path(match):
            # match.group(0)은 'package://Capsule_robot_description/' 전체
            # 우리는 이걸 지우고 실제 경로를 넣고 싶음
            # 하지만 보통 meshes 폴더는 프로젝트 루트 바로 아래에 있음.
            return project_root + "/"

        content = re.sub(r'package://[^/]+/', replace_package_path, content)
        
        # 혹시 file://$(find ...) 패턴이 있다면? (Fusion360 구버전 스타일)
        # file://$(find Capsule_robot_description)/meshes/...
        def replace_find_path(match):
            return "file://" + project_root + "/"
            
        content = re.sub(r'file://\$\(find [^)]+\)/', replace_find_path, content)


        # 3. 빈 줄 정리 (미관상)
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # 4. 저장
        output_path = os.path.join(current_dir, urdf_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"--- 변환 완료! ---")
        print(f"저장된 파일: {output_path}")
        print("이제 이 URDF 파일을 PyBullet에서 로드하시면 됩니다.")
        
    except FileNotFoundError:
        print(f"오류: '{xacro_filename}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    # 여기에 변환할 파일 이름을 적으세요
    input_file = "Capsule_robot.xacro"  # 원본 파일명
    output_file = "Capsule_robot.urdf"  # 생성할 파일명
    
    convert_xacro_to_urdf(input_file, output_file)