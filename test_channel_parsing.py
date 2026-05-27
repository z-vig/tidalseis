import re
from typing import Literal, TypeAlias
from dataclasses import dataclass

SEEDCodeCategory: TypeAlias = Literal[
    "ACE",
    "ACU",
    "BCI",
    "BH[ZNE]",
    "BH[1-n]",
    "BJ[ZNE]",
    "BL[ZNE]",
    "BN[ZNE]",
    "BN[1-n]",
    "EH[ZNE]",
    "EH[123]",
    "EL[ZNE]",
    "HD[IO]",
    "HH[ZNE]",
    "HJ[ZNE]",
    "HL[ZNE]",
    "HL[1-n]",
    "HN[ZNE] or HN[123456]",
    "LCE",
    "LCL",
    "LCQ",
    "LD[IO]",
    "LEB",
    "LEC",
    "LEP",
    "LH[ZNE]",
    "LH[12]",
    "LL[ZNE]",
    "LII",
    "LJ[ZNE]",
    "LKI",
    "LL[1-n]",
    "LN[ZNE] or LN[1-n]",
    "LOG",
    "LTW",
    "MH[ZNE]",
    "OCF",
    "SH[ZNE]",
    "UCD",
    "UCQ",
    "UEP",
    "UF[1...n]",
    "UFC",
    "UK2",
    "UM[ZNE] or UM[UVW]",
    "VCE",
    "VCO",
    "VCQ",
    "VD[IO]",
    "VEA",
    "VEC",
    "VEP",
    "VFP",
    "VH[ZNE]",
    "VK2",
    "VK[IO]",
    "VM[ZNE] or VM[UVW]",
    "VN[ZNE]",
]

CHANNEL_CODE_PATTERNS: dict[SEEDCodeCategory, re.Pattern[str]] = {
    "ACE": re.compile(r"^ACE$"),
    "ACU": re.compile(r"^ACU$"),
    "BCI": re.compile(r"^BCI$"),
    "BH[ZNE]": re.compile(r"^BH[ZNE]$"),
    "BH[1-n]": re.compile(r"^BH\d+$"),
    "BJ[ZNE]": re.compile(r"^BJ[ZNE]$"),
    "BL[ZNE]": re.compile(r"^BL[ZNE]$"),
    "BN[ZNE]": re.compile(r"^BN[ZNE]$"),
    "BN[1-n]": re.compile(r"^BN\d+$"),
    "EH[ZNE]": re.compile(r"^EH[ZNE]$"),
    "EH[123]": re.compile(r"^EH[123]$"),
    "EL[ZNE]": re.compile(r"^EL[ZNE]$"),
    "HD[IO]": re.compile(r"^HD[IO]$"),
    "HH[ZNE]": re.compile(r"^HH[ZNE]$"),
    "HJ[ZNE]": re.compile(r"^HJ[ZNE]$"),
    "HL[ZNE]": re.compile(r"^HL[ZNE]$"),
    "HL[1-n]": re.compile(r"^HL\d+$"),
    "HN[ZNE] or HN[123456]": re.compile(r"^HN[ZNE123456]$"),
    "LCE": re.compile(r"^LCE$"),
    "LCL": re.compile(r"^LCL$"),
    "LCQ": re.compile(r"^LCQ$"),
    "LD[IO]": re.compile(r"^LD[IO]$"),
    "LEB": re.compile(r"^LEB$"),
    "LEC": re.compile(r"^LEC$"),
    "LEP": re.compile(r"^LEP$"),
    "LH[ZNE]": re.compile(r"^LH[ZNE]$"),
    "LH[12]": re.compile(r"^LH[12]$"),
    "LL[ZNE]": re.compile(r"^LL[ZNE]$"),
    "LII": re.compile(r"^LII$"),
    "LJ[ZNE]": re.compile(r"^LJ[ZNE]$"),
    "LKI": re.compile(r"^LKI$"),
    "LL[1-n]": re.compile(r"^LL\d+$"),
    "LN[ZNE] or LN[1-n]": re.compile(r"^LN[ZNE\d+]$"),
    "LOG": re.compile(r"^LOG$"),
    "LTW": re.compile(r"^LTW$"),
    "MH[ZNE]": re.compile(r"^MH[ZNE]$"),
    "OCF": re.compile(r"^OCF$"),
    "SH[ZNE]": re.compile(r"^SH[ZNE]$"),
    "UCD": re.compile(r"^UCD$"),
    "UCQ": re.compile(r"^UCQ$"),
    "UEP": re.compile(r"^UEP$"),
    "UF[1...n]": re.compile(r"^UF\d+$"),
    "UFC": re.compile(r"^UFC$"),
    "UK2": re.compile(r"^UK2$"),
    "UM[ZNE] or UM[UVW]": re.compile(r"^UM[ZNEUVW]$"),
    "VCE": re.compile(r"^VCE$"),
    "VCO": re.compile(r"^VCO$"),
    "VCQ": re.compile(r"^VCQ$"),
    "VD[IO]": re.compile(r"^VD[IO]$"),
    "VEA": re.compile(r"^VEA$"),
    "VEC": re.compile(r"^VEC$"),
    "VEP": re.compile(r"^VEP$"),
    "VFP": re.compile(r"^VFP$"),
    "VH[ZNE]": re.compile(r"^VH[ZNE]$"),
    "VK2": re.compile(r"^VK2$"),
    "VK[IO]": re.compile(r"^VK[IO]$"),
    "VM[ZNE] or VM[UVW]": re.compile(r"^VM[ZNEUVW]$"),
    "VN[ZNE]": re.compile(r"^VN[ZNE]$"),
}


@dataclass
class SEEDCodeMetaData:
    code: str
    category: SEEDCodeCategory
    archive: str
    data_type: str
    config: str
    gain: str
    period: str
    desc: str


def get_code_category(code: str) -> SEEDCodeCategory:
    for k, v in CHANNEL_CODE_PATTERNS.items():
        if re.fullmatch(v, code):
            return k
    raise ValueError("Code does not match any category.")


def get_code_metadata(code: str, cat: SEEDCodeCategory) -> SEEDCodeMetaData:
    with open("./SEED_code_data.csv", "r") as f:
        for line in f.readlines():
            line_list = [i.strip() for i in line.split(",")]
            if line_list[0] == cat:
                return SEEDCodeMetaData(code, cat, *line_list[1:])
    raise ValueError("Code was not found in metadata table.")


code = "EPZ"
category = get_code_category(code)
meta = get_code_metadata(code, category)
print(meta)
