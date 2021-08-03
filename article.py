from dataclasses import dataclass
from typing import List
import datetime

@dataclass
class Section:
    title: str
    body: str
    def __str__(self):
        return self.title + '\n\n' + self.body


@dataclass
class Article:
    title: str
    date: datetime.date
    sections: List[Section]
    def __str__(self):
        return self.title + '\n\n' + '\n'.join(str(section) for section in self.sections)
