predict_two_level1.0.py
- base modified cosmos predictor. Updates PHT as it goes and relies on LRU to clear pattern.

predict_two_level_2.0.py
- modified base predictor. Updates, PHT with History of readers

predict_two_level_3.0.py
- modified base predictor. Each reader upgrades bit, 
- could use history to downgrade or could simply rely on LRU to clear.

predict_two_level_4.0.py
- modified 2.0 that upgrades PHT with entire history.

grep "pattern" file.txt | wc -l
