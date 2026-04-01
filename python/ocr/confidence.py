"""Smart Confidence Retry — re-processes low-confidence words."""

from __future__ import annotations

from PIL import Image

from ocr.engine import OCREngine, PageResult, WordResult

PADDING = 4  # pixels of padding around cropped word region


class ConfidenceRetry:
    def __init__(self, engine: OCREngine, threshold: float = 60.0):
        self._engine = engine
        self._threshold = threshold

    def retry_low_confidence(
        self,
        image: Image.Image,
        page_result: PageResult
    ) -> PageResult:
        """Re-run OCR on low-confidence words; replace if improved."""
        if not page_result.words:
            return page_result

        img_w, img_h = image.size
        improved_words: list[WordResult] = []

        for word in page_result.words:
            if word.conf >= self._threshold:
                improved_words.append(word)
                continue

            # Crop the word region with padding
            x0 = max(0, word.left - PADDING)
            y0 = max(0, word.top - PADDING)
            x1 = min(img_w, word.left + word.width + PADDING)
            y1 = min(img_h, word.top + word.height + PADDING)

            if x1 <= x0 or y1 <= y0:
                improved_words.append(word)
                continue

            crop = image.crop((x0, y0, x1, y1))

            # Try PSM 8 (single word) then PSM 10 (single character)
            best_word = word
            for psm in (8, 10):
                data = self._engine.run_on_region(crop, psm=psm)
                retry_words = self._extract_best_word(data)
                if retry_words and retry_words[0].conf > best_word.conf:
                    # Restore original coordinates
                    w = retry_words[0]
                    best_word = WordResult(
                        text=w.text,
                        conf=w.conf,
                        left=word.left,
                        top=word.top,
                        width=word.width,
                        height=word.height
                    )
                    if best_word.conf >= self._threshold:
                        break

            improved_words.append(best_word)

        # Rebuild page result with improved words
        confidences = [w.conf for w in improved_words if w.conf >= 0]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        plain_text = ' '.join(w.text for w in improved_words)

        return PageResult(
            page_num=page_result.page_num,
            words=improved_words,
            plain_text=plain_text,
            avg_confidence=round(avg_conf, 2),
            dominant_language=page_result.dominant_language
        )

    def _extract_best_word(self, data: dict) -> list[WordResult]:
        words = []
        n = len(data['text'])
        for i in range(n):
            text = data['text'][i].strip()
            conf = float(data['conf'][i])
            if not text or conf < 0:
                continue
            words.append(WordResult(
                text=text,
                conf=conf,
                left=data['left'][i],
                top=data['top'][i],
                width=data['width'][i],
                height=data['height'][i]
            ))
        # Return the highest-confidence word
        return sorted(words, key=lambda w: w.conf, reverse=True)[:1]
