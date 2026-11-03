"""Independent structural tests for paired SASS listing comparator (synthetic only)."""
import unittest
from research.v317.paired_sass_listing_transfer import parse_listing, PC, CONTROL, REGISTER

HEADER = "code for sm_80\nFunction : test_kernel\n"

def listing(modifier, control):
    return (HEADER + f"/*0000*/ LDG.{modifier} R2, [R3.64] ; /* 0x0123456789abcdef */\n"
            + f"          /* {control} */\n"
            + "/*0010*/ FFMA R4, R5, R6, R7 ; /* 0x1111111111111111 */\n"
            + "          /* 0x2222222222222222 */\n")

class PairAuditTests(unittest.TestCase):
    def test_modifier_control_difference_preserves_register_tokens(self):
        a = parse_listing(listing("E.EF.128", "0x0000000000000001"))
        b = parse_listing(listing("E.128", "0x0000000000000002"))
        self.assertEqual(set(a), set(b))
        self.assertNotEqual(a["0000"]["instruction"], b["0000"]["instruction"])
        self.assertEqual(a["0000"]["word"], b["0000"]["word"])
        self.assertNotEqual(a["0000"]["control"], b["0000"]["control"])
        self.assertEqual(REGISTER.findall(a["0000"]["instruction"]),
                         REGISTER.findall(b["0000"]["instruction"]))

    def test_reject_duplicate_pc(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            parse_listing(listing("E.128", "0x0000000000000001") * 2)

    def test_reject_missing_header_or_encoding(self):
        with self.assertRaisesRegex(ValueError, "header"):
            parse_listing("/*0000*/ MOV R1, R2 ; /* 0x1 */\n/* 0x2 */")
        with self.assertRaisesRegex(ValueError, "missing control"):
            parse_listing(HEADER + "/*0000*/ MOV R1, R2 ; /* 0x1 */\n")

    def test_independent_line_shapes(self):
        self.assertTrue(PC.fullmatch("/*0010*/ FFMA R1, R2, R3, R4 ; /* 0xabcdef */"))
        self.assertTrue(CONTROL.fullmatch("    /* 0xabcdef */"))
        self.assertEqual(REGISTER.findall("FFMA R1, R2.reuse, R3, RZ"),
                         ["R1", "R2.reuse", "R3", "RZ"])

if __name__ == "__main__":
    unittest.main()
