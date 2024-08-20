from typing import List, Dict, Any, Union, Literal, OrderedDict, Tuple
from dataclasses import dataclass
import numpy as np

AssetCategory = Literal['text', 'facade', 'interior',
                    'floorplan', 'section', 'detail', 'birdview', 'other']

@dataclass
class BaseQuestion:
    theme: str
    content: str = None

    def __hash__(self) -> int:
        return hash(self.content)
    
    def __str__(self) -> str:
        return self.content


@dataclass
class AssetItem:
    """
    Used in: (1) preparing the vision model call (2) storing the results
    """
    case_id: int
    asset_path: str
    category: AssetCategory
    answers: OrderedDict[BaseQuestion, List[str]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'asset_path': self.asset_path,
            'category': self.category,
            'answers': {q.theme: a for q, a in self.answers.items()}
        }
    
@dataclass
class RawTextItem:
    case_id: int
    asset_path: str
    raw_content: str
    chunked_content: List[str]
    category: AssetCategory = "text"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'chunked_content': self.chunked_content,
        }
    
@dataclass
class DesignCase:
    case_id: int
    name: str
    folder_path: str
    web_link: str
    content: List[Union[AssetItem, RawTextItem]]

    # generated during preprocessing
    embeddings: np.ndarray = None
    all_texts: List[str] = None
    content_to_emb_idx: Dict[int, List[int]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'case_id': self.case_id,
            'name': self.name,
            'folder_path': self.folder_path,
            'web_link': self.web_link,
            'content': [item.to_dict() for item in self.content],
        }
    
    def get_all_text(self) -> List[str]:
        results = []
        indices = {}
        for item_idx, item in enumerate(self.content):
            start_idx = len(results)
            if isinstance(item, RawTextItem):
                results.extend(item.chunked_content)
            else:
                for q in item.answers:
                    results.extend(item.answers[q])
            indices[item_idx] = list(range(start_idx, len(results)))
        self.content_to_emb_idx = indices
        self.all_texts = results
        return results
    
    def get_emb_mask(self, 
                     focus_category: List[AssetCategory],
                     text_only: bool = False,
                     ) -> np.ndarray:
        """
        Get the mask for the embeddings
        """
        if text_only:
            item_mask = [isinstance(item, RawTextItem) for item in self.content]
        else:
            item_mask = [item.category in focus_category for item in self.content]
        # Get the mask for the embeddings
        emb_mask = np.zeros(self.embeddings.shape[0], dtype=bool)
        for item_idx, mask in enumerate(item_mask):
            if mask:
                emb_mask[self.content_to_emb_idx[item_idx]] = True
        return emb_mask
    
    def look_up_content(self, emb_idx) -> Tuple[Union[RawTextItem, AssetItem], str]:
        for item_idx, emb_indices in self.content_to_emb_idx.items():
            if emb_idx in emb_indices:
                return self.content[item_idx], self.all_texts[emb_idx]
        return None

    
@dataclass
class CaseDatabase:
    cases: OrderedDict[str, DesignCase]
    

@dataclass
class EnrichedQuery:
    raw: str
    concentrate: List[Tuple[List[AssetCategory], List[str]]]


@dataclass
class RetrievalResult:
    case_id: int
    name: str
    score: float
    url: str
    score_by_concentrate: List[float]
    max_entry_by_concentrate: List[str]
    max_item_by_concentrate: List[Union[RawTextItem, AssetItem]]
