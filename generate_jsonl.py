#!/usr/bin/env python3
"""
.depファイルからjsonlを生成するスクリプト
各.depファイルから親子関係を抽出してJSON Lines形式で出力する
"""

import json
import os
from pathlib import Path


def parse_dep_file(file_path):
    """
    .depファイルを解析して親子関係のリストを返す
    
    Args:
        file_path: .depファイルのパス
    
    Returns:
        list: [{"child": child_id, "parent": parent_id}, ...] の辞書のリスト
    """
    oyako = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # 行の形式: "1:1 3:3 [0.0, 6.056] [80.108, 88.898] Background"
            parts = line.split()
            if len(parts) < 2:
                continue
            
            # "1:1" から子ID、"3:3" から親IDを取得
            child_part = parts[0]  # "1:1"
            parent_part = parts[1]  # "3:3"
            
            # コロンの後の数字を取得
            child_id = int(child_part.split(':')[1])
            parent_id = int(parent_part.split(':')[1])
            
            oyako.append({"child": child_id, "parent": parent_id})
    
    return oyako


def generate_jsonl(dep_dir, output_file):
    """
    dep_sentディレクトリ内の全ての.depファイルを処理してjsonlを生成
    
    Args:
        dep_dir: .depファイルが格納されているディレクトリのパス
        output_file: 出力するjsonlファイルのパス
    """
    dep_dir = Path(dep_dir)
    
    # .depファイルを取得して数値でソート
    dep_files = sorted(dep_dir.glob('*.dep'), key=lambda x: int(x.stem))
    
    with open(output_file, 'w', encoding='utf-8') as out:
        for dep_file in dep_files:
            # ファイル名から video_id を取得 (例: "003.dep" -> "003")
            video_id = dep_file.stem
            
            # 親子関係を解析
            oyako = parse_dep_file(dep_file)
            
            # JSON形式で出力
            data = {
                "video_id": video_id,
                "child_parent": oyako
            }
            
            # JSON Linesとして1行ずつ出力
            out.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    print(f"✅ 生成完了: {output_file}")
    print(f"📊 処理したファイル数: {len(dep_files)}")


def main():
    # dep_sentディレクトリのパス
    script_dir = Path(__file__).parent
    dep_dir = script_dir / 'dep_sent'
    output_file = script_dir / 'child_parent.jsonl'
    
    if not dep_dir.exists():
        print(f"❌ エラー: {dep_dir} が見つかりません")
        return
    
    generate_jsonl(dep_dir, output_file)


if __name__ == '__main__':
    main()
