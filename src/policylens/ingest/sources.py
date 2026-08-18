from dataclasses import dataclass
from pathlib import Path

from policylens.config import RAW_DIR


@dataclass(frozen=True)
class Source:
    """A single Dataful commodity price dataset, manually purchased and landed in data/raw/."""

    dataset_id: int
    commodity: str
    zip_path_override: Path | None = None
    """Set only in tests, to point a Source at a fixture zip instead of data/raw/."""

    @property
    def zip_path(self) -> Path:
        if self.zip_path_override is not None:
            return self.zip_path_override
        return RAW_DIR / f"{self.dataset_id}- Dataful.zip"


SOURCES: list[Source] = [
    Source(19929, "Wheat"),
    Source(19930, "Vanaspati (Packed)"),
    Source(19932, "Tur/Arhar Dal"),
    Source(19934, "Tea (Loose)"),
    Source(19935, "Sunflower Oil (Packed)"),
    Source(19936, "Sugar"),
    Source(19937, "Soya Oil (Packed)"),
    Source(19938, "Salt (Iodised, Packed)"),
    Source(19939, "Rice"),
    Source(19941, "Palm Oil (Packed)"),
    Source(19942, "Onion"),
    Source(19943, "Mustard Oil (Packed)"),
    Source(19944, "Moong Dal"),
    Source(19945, "Milk"),
    Source(19946, "Masoor Dal"),
    Source(19948, "Groundnut Oil (Packed)"),
    Source(19950, "Atta (Wheat flour)"),
]
