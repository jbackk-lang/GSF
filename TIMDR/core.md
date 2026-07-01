# GSF/TIMDR — ciągłość danych finansowych

TIMDR w GSF definiuje, które informacje w globalnym systemie finansowym
muszą być ciągłe, żeby pole było stabilne.

Główna idea:
- dane nie mogą się „urwać” między krajami, sektorami, instytucjami,
- każde pole (np. dług, stopy procentowe, przepływy kapitału) musi mieć
  spójny ciąg w czasie i przestrzeni,
- przerwanie ciągłości jest traktowane jako błąd struktury, nie tylko brak danych.

TIMDR w tym module:
- identyfikuje przerwania (breaks),
- wskazuje brakujące odcinki (gaps),
- oznacza nadmiarowe węzły (over-nodes),
- buduje mapę ciągłości dla kluczowych pól finansowych.
