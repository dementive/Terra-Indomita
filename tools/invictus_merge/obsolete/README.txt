Obsolete. 000_indomita_merge_fix.py renumbered characters with regexes that lacked word
boundaries and also matched `c:Y35 = {`, which corrupted Invictus references (e.g. Philip II
char:35 became char:714). Kept for history only; use ../audit_chars.py and ../repair.py instead.
