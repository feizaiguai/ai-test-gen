#!/usr/bin/env python3
"""
AI Test Generator - 智能测试用例生成器
分析代码函数签名和逻辑自动生成单元测试
"""

import ast
import os
import sys
from typing import List, Dict, Any, Optional
from colorama import init, Fore, Style

init(autoreset=True)


class TestGenerator:
    """测试用例生成器"""
    
    def __init__(self, framework: str = 'pytest'):
        self.framework = framework  # pytest or jest
        self.test_cases = []
    
    def generate_from_file(self, filepath: str) -> str:
        """从文件生成测试"""
        if not os.path.exists(filepath):
            print(f"{Fore.RED}错误: 文件不存在 - {filepath}")
            return ""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            ext = os.path.splitext(filepath)[1].lower()
            
            print(f"{Fore.CYAN}正在分析: {filepath}")
            
            if ext == '.py':
                return self._generate_python_tests(filepath, code)
            elif ext in ['.js', '.ts']:
                return self._generate_javascript_tests(filepath, code)
            else:
                return f"// 不支持的文件类型: {ext}\n"
                
        except Exception as e:
            print(f"{Fore.RED}生成失败: {str(e)}")
            return ""
    
    def _generate_python_tests(self, filepath: str, code: str) -> str:
        """生成 Python pytest 测试"""
        tests = []
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        
        tests.append("import pytest\n")
        tests.append(f"from {module_name} import *\n\n")
        
        try:
            tree = ast.parse(code)
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.col_offset == 0 and not node.name.startswith('_'):
                        functions.append(node)
                elif isinstance(node, ast.ClassDef):
                    if node.col_offset == 0:
                        classes.append(node)
            
            # 生成函数测试
            for func in functions:
                test = self._generate_function_test(func, module_name)
                tests.append(test)
            
            # 生成类测试
            for cls in classes:
                test = self._generate_class_test(cls, module_name)
                tests.append(test)
            
        except SyntaxError as e:
            tests.append(f"# 语法错误: {e}\n")
        
        return ''.join(tests)
    
    def _generate_function_test(self, func: ast.FunctionDef, module: str) -> str:
        """生成函数测试"""
        func_name = func.name
        args = [arg.arg for arg in func.args.args]
        
        lines = []
        lines.append(f"def test_{func_name}():\n")
        lines.append(f'    """测试 {func_name} 函数"""\n')
        
        if args:
            # 简单测试用例
            test_args = ', '.join(['None' if i == 0 else 'None' for i in range(len(args))])
            lines.append(f"    result = {func_name}({test_args})\n")
        else:
            lines.append(f"    result = {func_name}()\n")
        
        lines.append("    # 断言结果\n")
        lines.append("    assert result is not None\n\n")
        
        return ''.join(lines)
    
    def _generate_class_test(self, cls: ast.ClassDef, module: str) -> str:
        """生成类测试"""
        lines = []
        lines.append(f"class Test{cls.name}:\n")
        lines.append(f'    """测试 {cls.name} 类"""\n\n')
        
        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
        
        for method in methods:
            if method.name.startswith('_') and method.name != '__init__':
                continue
            
            method_name = method.name
            args = [arg.arg for arg in method.args.args]
            
            lines.append(f"    def test_{method_name}(self):\n")
            lines.append(f'        """测试 {method_name} 方法"""\n')
            
            if method_name == '__init__':
                test_args = ', '.join(['None' for _ in range(len(args)-1)])  # 减去 self
                lines.append(f"        instance = {cls.name}({test_args})\n")
                lines.append("        assert instance is not None\n\n")
            else:
                test_args = ', '.join(['None' for _ in range(len(args)-1)])  # 减去 self
                lines.append(f"        result = {cls.name}().{method_name}({test_args})\n")
                lines.append("        assert result is not None\n\n")
        
        return ''.join(lines)
    
    def _generate_javascript_tests(self, filepath: str, code: str) -> str:
        """生成 JavaScript Jest 测试"""
        tests = []
        filename = os.path.splitext(os.path.basename(filepath))[0]
        
        tests.append(f"const {filename} = require('./{filename}');\n\n")
        
        # 简单解析函数
        functions = []
        function_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|(?:async\s+)?function\s+(\w+))'
        
        for match in re.finditer(function_pattern, code):
            func_name = match.group(1) or match.group(2) or match.group(3)
            if func_name and func_name not in ['describe', 'test', 'it', 'expect']:
                functions.append(func_name)
        
        for func_name in functions[:5]:  # 最多生成5个测试
            tests.append(f"describe('{func_name}', () => {{\n")
            tests.append(f"  test('should work', () => {{\n")
            tests.append(f"    const result = {func_name}();\n")
            tests.append("    expect(result).toBeDefined();\n")
            tests.append("  });\n")
            tests.append("});\n\n")
        
        return ''.join(tests)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}使用方法: python main.py <代码文件> [框架]")
        print(f"示例: python main.py example.py pytest")
        print(f"示例: python main.py example.js jest")
        sys.exit(1)
    
    filepath = sys.argv[1]
    framework = sys.argv[2] if len(sys.argv) > 2 else 'pytest'
    
    generator = TestGenerator(framework)
    tests = generator.generate_from_file(filepath)
    
    if tests:
        print(f"\n{Fore.GREEN}生成的测试代码:\n")
        print(tests)
        
        # 保存测试文件
        ext = os.path.splitext(filepath)[1]
        base = os.path.splitext(os.path.basename(filepath))[0]
        
        if ext == '.py':
            test_file = f"test_{base}.py"
        else:
            test_file = f"{base}.test.js"
        
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(tests)
            print(f"{Fore.GREEN}✓ 测试文件已保存: {test_file}")
        except Exception as e:
            print(f"{Fore.YELLOW}保存失败: {str(e)}")


if __name__ == '__main__':
    import re
    main()
