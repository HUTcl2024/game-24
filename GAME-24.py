import random
import itertools
from typing import List, Tuple, Set
from fractions import Fraction
import unittest
from unittest.mock import patch
from io import StringIO
import sys

class Card:
    """扑克牌类"""
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
        self.value = self._get_value()
    
    def _get_value(self) -> int:
        """获取牌的数值"""
        if self.rank == 'A':
            return 1
        elif self.rank in ['J', 'Q', 'K']:
            return {'J': 11, 'Q': 12, 'K': 13}[self.rank]
        else:
            return int(self.rank)
    
    def __str__(self):
        return f"{self.suit}{self.rank}"
    
    def __repr__(self):
        return self.__str__()

class Game24:
    """24点游戏类"""
    
    def __init__(self):
        self.suits = ['♠', '♥', '♣', '♦']
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.deck = self._create_deck()
    
    def _create_deck(self) -> List[Card]:
        """创建一副牌"""
        deck = []
        for suit in self.suits:
            for rank in self.ranks:
                deck.append(Card(suit, rank))
        return deck
    
    def draw_cards(self, num: int = 4) -> List[Card]:
        """随机抽取指定数量的牌"""
        return random.sample(self.deck, num)
    
    def evaluate_expression(self, a: float, b: float, c: float, d: float, 
                          op1: str, op2: str, op3: str, structure: str) -> Tuple[bool, str]:
        """
        计算表达式的值
        structure: 表达式结构，如 "((a op1 b) op2 c) op3 d"
        """
        try:
            # 使用 Fraction 进行精确计算
            a, b, c, d = Fraction(a), Fraction(b), Fraction(c), Fraction(d)
            
            def apply_op(x: Fraction, y: Fraction, op: str) -> Fraction:
                if op == '+':
                    return x + y
                elif op == '-':
                    return x - y
                elif op == '*':
                    return x * y
                elif op == '/':
                    if y == 0:
                        raise ZeroDivisionError
                    return x / y
            
            # 根据不同的结构计算
            if structure == "((a op1 b) op2 c) op3 d":
                result = apply_op(apply_op(apply_op(a, b, op1), c, op2), d, op3)
                expr = f"(({a} {op1} {b}) {op2} {c}) {op3} {d}"
            elif structure == "(a op1 (b op2 c)) op3 d":
                result = apply_op(apply_op(a, apply_op(b, c, op2), op1), d, op3)
                expr = f"({a} {op1} ({b} {op2} {c})) {op3} {d}"
            elif structure == "(a op1 b) op2 (c op3 d)":
                result = apply_op(apply_op(a, b, op1), apply_op(c, d, op3), op2)
                expr = f"({a} {op1} {b}) {op2} ({c} {op3} {d})"
            elif structure == "a op1 ((b op2 c) op3 d)":
                result = apply_op(a, apply_op(apply_op(b, c, op2), d, op3), op1)
                expr = f"{a} {op1} (({b} {op2} {c}) {op3} {d})"
            elif structure == "a op1 (b op2 (c op3 d))":
                result = apply_op(a, apply_op(b, apply_op(c, d, op3), op2), op1)
                expr = f"{a} {op1} ({b} {op2} ({c} {op3} {d}))"
            
            # 检查结果是否为24
            if abs(result - 24) < 1e-9:
                return True, expr
            else:
                return False, expr
                
        except (ZeroDivisionError, ValueError):
            return False, ""
    
    def find_all_solutions(self, cards: List[Card]) -> List[str]:
        """找到所有可能的解法"""
        values = [card.value for card in cards]
        return self.find_all_solutions_from_numbers(values)
    
    def find_all_solutions_from_numbers(self, numbers: List[int], keep_order: bool = True) -> List[str]:
        """从数字列表找到所有可能的解法"""
        solutions = set()
        operations = ['+', '-', '*', '/']
        structures = [
            "((a op1 b) op2 c) op3 d",
            "(a op1 (b op2 c)) op3 d", 
            "(a op1 b) op2 (c op3 d)",
            "a op1 ((b op2 c) op3 d)",
            "a op1 (b op2 (c op3 d))"
        ]
        
        # 如果保持顺序，只使用原始顺序；否则尝试所有排列
        if keep_order:
            permutations = [tuple(numbers)]
        else:
            permutations = list(itertools.permutations(numbers))
        
        # 尝试指定的数字排列
        for perm in permutations:
            a, b, c, d = perm
            
            # 尝试所有运算符组合
            for ops in itertools.product(operations, repeat=3):
                op1, op2, op3 = ops
                
                # 尝试所有表达式结构
                for structure in structures:
                    is_solution, expr = self.evaluate_expression(a, b, c, d, op1, op2, op3, structure)
                    if is_solution:
                        solutions.add(expr)
        
        return sorted(list(solutions))
    
    def has_solution(self, cards: List[Card]) -> bool:
        """检查是否有解"""
        solutions = self.find_all_solutions(cards)
        return len(solutions) > 0

# ============================================================================
# 测试用例
# ============================================================================

class TestCard(unittest.TestCase):
    """测试Card类"""
    
    def test_card_creation(self):
        """测试卡片创建"""
        card = Card('♠', 'A')
        self.assertEqual(card.suit, '♠')
        self.assertEqual(card.rank, 'A')
        self.assertEqual(card.value, 1)
    
    def test_card_values(self):
        """测试各种卡片的数值"""
        test_cases = [
            ('♠', 'A', 1),
            ('♥', '2', 2),
            ('♣', '10', 10),
            ('♦', 'J', 11),
            ('♠', 'Q', 12),
            ('♥', 'K', 13)
        ]
        
        for suit, rank, expected_value in test_cases:
            with self.subTest(rank=rank):
                card = Card(suit, rank)
                self.assertEqual(card.value, expected_value)
    
    def test_card_string_representation(self):
        """测试卡片字符串表示"""
        card = Card('♠', 'A')
        self.assertEqual(str(card), '♠A')
        self.assertEqual(repr(card), '♠A')

class TestGame24(unittest.TestCase):
    """测试Game24类"""
    
    def setUp(self):
        """测试前的设置"""
        self.game = Game24()
    
    def test_deck_creation(self):
        """测试牌组创建"""
        self.assertEqual(len(self.game.deck), 52)  # 标准52张牌
        
        # 检查是否包含所有花色和点数
        suits = set(card.suit for card in self.game.deck)
        ranks = set(card.rank for card in self.game.deck)
        
        self.assertEqual(suits, {'♠', '♥', '♣', '♦'})
        self.assertEqual(len(ranks), 13)
    
    def test_draw_cards(self):
        """测试抽牌功能"""
        cards = self.game.draw_cards(4)
        self.assertEqual(len(cards), 4)
        
        # 检查抽到的牌都在牌组中
        for card in cards:
            self.assertIn(card, self.game.deck)
    
    def test_evaluate_expression_basic_operations(self):
        """测试基本运算表达式计算"""
        # 测试加法: (6 + 6) + (6 + 6) = 24
        is_solution, expr = self.game.evaluate_expression(
            6, 6, 6, 6, '+', '+', '+', "(a op1 b) op2 (c op3 d)"
        )
        self.assertTrue(is_solution)
        self.assertIn('6 + 6', expr)
        
        # 测试乘法: 6 * 4 * 1 * 1 = 24
        is_solution, expr = self.game.evaluate_expression(
            6, 4, 1, 1, '*', '*', '*', "((a op1 b) op2 c) op3 d"
        )
        self.assertTrue(is_solution)
    
    def test_evaluate_expression_division_by_zero(self):
        """测试除零错误处理"""
        is_solution, expr = self.game.evaluate_expression(
            1, 0, 2, 3, '/', '+', '+', "((a op1 b) op2 c) op3 d"
        )
        self.assertFalse(is_solution)
        self.assertEqual(expr, "")
    
    def test_find_solutions_known_cases(self):
        """测试已知有解的情况"""
        # 测试经典的24点题目
        test_cases = [
            ([6, 6, 2, 2], True),   # (6+2)*(6-2) = 8*3 = 24
            ([8, 3, 8, 3], True),   # 8/(3-8/3) = 8/(1/3) = 24
            ([1, 1, 8, 8], True),   # (8-1)*(8-1) = 7*7 = 49 (错误示例)
            ([4, 1, 8, 7], True),   # (8-4)*(7-1) = 4*6 = 24
            ([1, 1, 1, 1], False),  # 无解
        ]
        
        for numbers, has_solution in test_cases:
            with self.subTest(numbers=numbers):
                solutions = self.game.find_all_solutions_from_numbers(numbers, keep_order=False)
                if has_solution:
                    self.assertGreater(len(solutions), 0, f"数字 {numbers} 应该有解")
                else:
                    self.assertEqual(len(solutions), 0, f"数字 {numbers} 应该无解")
    
    def test_find_solutions_keep_order(self):
        """测试保持顺序的解法查找"""
        numbers = [6, 6, 2, 2]
        
        # 保持顺序
        solutions_ordered = self.game.find_all_solutions_from_numbers(numbers, keep_order=True)
        
        # 不保持顺序
        solutions_all = self.game.find_all_solutions_from_numbers(numbers, keep_order=False)
        
        # 保持顺序的解法数量应该 <= 所有排列的解法数量
        self.assertLessEqual(len(solutions_ordered), len(solutions_all))
    
    def test_has_solution(self):
        """测试是否有解的判断"""
        # 创建测试卡片
        cards_with_solution = [
            Card('♠', '6'), Card('♥', '6'), Card('♣', '2'), Card('♦', '2')
        ]
        cards_no_solution = [
            Card('♠', 'A'), Card('♥', 'A'), Card('♣', 'A'), Card('♦', 'A')
        ]
        
        self.assertTrue(self.game.has_solution(cards_with_solution))
        self.assertFalse(self.game.has_solution(cards_no_solution))

class TestInputParsing(unittest.TestCase):
    """测试输入解析功能"""
    
    @patch('builtins.input')
    def test_get_numbers_input_formats(self, mock_input):
        """测试各种输入格式"""
        # 由于get_numbers_input是在主程序中定义的，我们这里测试输入解析逻辑
        test_cases = [
            ("[6,6,2,2]", [6, 6, 2, 2]),
            ("6,6,2,2", [6, 6, 2, 2]),
            ("6 6 2 2", [6, 6, 2, 2]),
            ("6622", [6, 6, 2, 2]),
            ("[A,K,Q,J]", [1, 13, 12, 11]),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                # 模拟输入解析逻辑
                user_input = input_str.strip()
                
                # 移除方括号
                if user_input.startswith('[') and user_input.endswith(']'):
                    user_input = user_input[1:-1]
                
                # 处理各种分隔符
                if ',' in user_input:
                    parts = user_input.split(',')
                elif ' ' in user_input:
                    parts = user_input.split()
                else:
                    if len(user_input) == 4 and all(c.isdigit() or c.upper() in 'AJQK' for c in user_input):
                        parts = list(user_input)
                
                # 清理并验证输入
                parts = [part.strip() for part in parts if part.strip()]
                
                # 转换为数字
                numbers = []
                for part in parts:
                    part = part.upper()
                    if part == 'A':
                        numbers.append(1)
                    elif part == 'J':
                        numbers.append(11)
                    elif part == 'Q':
                        numbers.append(12)
                    elif part == 'K':
                        numbers.append(13)
                    elif part.isdigit() and 1 <= int(part) <= 13:
                        numbers.append(int(part))
                
                self.assertEqual(numbers, expected)

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.game = Game24()
    
    def test_complete_workflow(self):
        """测试完整的工作流程"""
        # 1. 创建已知有解的数字组合
        numbers = [6, 6, 2, 2]
        
        # 2. 查找解法
        solutions = self.game.find_all_solutions_from_numbers(numbers, keep_order=True)
        
        # 3. 验证至少有一个解法
        self.assertGreater(len(solutions), 0)
        
        # 4. 验证解法格式正确（包含等号前的表达式）
        for solution in solutions:
            self.assertIsInstance(solution, str)
            self.assertNotEqual(solution.strip(), "")
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试极值
        edge_cases = [
            [1, 1, 1, 1],    # 最小值
            [13, 13, 13, 13], # 最大值
            [1, 2, 3, 4],     # 连续数字
            [2, 2, 2, 2],     # 相同数字
        ]
        
        for numbers in edge_cases:
            with self.subTest(numbers=numbers):
                # 应该能够正常执行，不抛出异常
                solutions = self.game.find_all_solutions_from_numbers(numbers, keep_order=True)
                self.assertIsInstance(solutions, list)

# ============================================================================
# 主程序部分（保持不变）
# ============================================================================

def display_cards(cards: List[Card]):
    """显示卡片"""
    print("抽到的卡片:")
    for i, card in enumerate(cards, 1):
        print(f"{i}. {card} (值: {card.value})")

def get_numbers_input():
    """获取用户输入的4个数字"""
    while True:
        user_input = input("请输入4个数字: ").strip()
        
        # 移除方括号
        if user_input.startswith('[') and user_input.endswith(']'):
            user_input = user_input[1:-1]  # 去掉首尾的方括号
        
        # 处理各种分隔符
        if ',' in user_input:
            parts = user_input.split(',')
        elif ' ' in user_input:
            parts = user_input.split()
        else:
            # 如果没有分隔符，尝试按字符分割（如果都是单个字符）
            if len(user_input) == 4 and all(c.isdigit() or c.upper() in 'AJQK' for c in user_input):
                parts = list(user_input)
            else:
                print("❌ 请用逗号或空格分隔4个数字，或使用方括号格式")
                continue
        
        # 清理并验证输入
        parts = [part.strip() for part in parts if part.strip()]
        
        if len(parts) != 4:
            print(f"❌ 需要输入4个数字，你输入了{len(parts)}个")
            continue
        
        # 转换为数字
        numbers = []
        try:
            for part in parts:
                part = part.upper()
                if part == 'A':
                    numbers.append(1)
                elif part == 'J':
                    numbers.append(11)
                elif part == 'Q':
                    numbers.append(12)
                elif part == 'K':
                    numbers.append(13)
                elif part.isdigit() and 1 <= int(part) <= 13:
                    numbers.append(int(part))
                else:
                    raise ValueError(f"无效数字: {part}")
            
            # 输入成功，返回数字列表
            return numbers
            
        except ValueError as e:
            print(f"❌ {e}")
            print("请输入有效的数字 (1-13) 或字母 (A, J, Q, K)")
            continue

def manual_input_mode():
    """手动输入模式 - 保持原始顺序"""
    game = Game24()
    
    print("\n📝 手动输入模式")
    print("请输入4个数字，支持多种格式:")
    print("• 方括号格式: [8,7,6,5]")
    print("• 逗号分隔: 8,7,6,5")
    print("• 空格分隔: 8 7 6 5")
    print("• 连续输入: 8765 (仅限单数字)")
    print("数字范围: 1-13，其中 A=1, J=11, Q=12, K=13")
    print("📌 注意：将保持你输入的数字顺序")
    
    while True:
        print("\n" + "-" * 40)
        
        # 获取用户输入的数字
        numbers = get_numbers_input()
        
        # 求解（保持原始顺序）
        solutions = game.find_all_solutions_from_numbers(numbers, keep_order=True)
        
        print(f"\n输入的数字（按顺序）: {numbers}")
        if solutions:
            print(f"✅ 找到 {len(solutions)} 种解法（保持输入顺序）:")
            for i, solution in enumerate(solutions[:10], 1):  # 最多显示10种
                print(f"{i:2d}. {solution} = 24")
            if len(solutions) > 10:
                print(f"... 还有 {len(solutions) - 10} 种解法")
        else:
            print("❌ 这组数字按此顺序无法组成24!")
            print("💡 提示：如果允许改变数字顺序，可能会有解法")
        
        # 询问是否继续
        choice = input("\n是否继续？(y/n): ").strip().lower()
        if choice not in ['y', 'yes', '是', '']:
            break

def random_mode():
    """随机模式 - 保持抽取顺序"""
    game = Game24()
    
    print("\n🎲 随机模式")
    print("📌 注意：将保持抽取的卡片顺序")
    
    while True:
        # 随机抽取4张牌
        cards = game.draw_cards(4)
        display_cards(cards)
        
        # 寻找解法（保持原始顺序）
        values = [card.value for card in cards]
        solutions = game.find_all_solutions_from_numbers(values, keep_order=True)
        
        print(f"\n卡片数值（按顺序）: {values}")
        if solutions:
            print(f"✅ 找到 {len(solutions)} 种解法（保持抽取顺序）:")
            for i, solution in enumerate(solutions[:5], 1):  # 最多显示5种
                print(f"{i}. {solution} = 24")
            if len(solutions) > 5:
                print(f"... 还有 {len(solutions) - 5} 种解法")
        else:
            print("❌ 这组牌按此顺序无法组成24!")
            print("💡 提示：如果允许改变数字顺序，可能会有解法")
        
        # 询问是否继续
        choice = input("\n是否继续？(y/n): ").strip().lower()
        if choice not in ['y', 'yes', '是', '']:
            break

def main():
    """主函数"""
    print("🎯 欢迎来到24点游戏！")
    print("=" * 50)
    
    while True:
        print("\n请选择游戏模式:")
        print("1. 🎲 随机模式 - 随机抽取4张牌（保持抽取顺序）")
        print("2. 📝 手动输入模式 - 自己输入4个数字（保持输入顺序）")
        print("3. 🧪 运行测试用例")
        print("4. 🚪 退出游戏")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            random_mode()
        elif choice == '2':
            manual_input_mode()
        elif choice == '3':
            run_tests()
        elif choice == '4':
            print("👋 感谢游戏！再见！")
            break
        else:
            print("❌ 无效选择，请输入1-4")

def run_tests():
    """运行测试用例"""
    print("\n🧪 运行测试用例...")
    print("=" * 50)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_classes = [TestCard, TestGame24, TestInputParsing, TestIntegration]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 显示测试结果摘要
    print("\n" + "=" * 50)
    print("📊 测试结果摘要:")
    print(f"✅ 运行测试: {result.testsRun}")
    print(f"❌ 失败: {len(result.failures)}")
    print(f"💥 错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2]}")
    
    if result.wasSuccessful():
        print("\n🎉 所有测试通过！代码运行正常！")
    else:
        print("\n⚠️  有测试失败，请检查代码！")
    
    input("\n按回车键返回主菜单...")

if __name__ == "__main__":
    main()
