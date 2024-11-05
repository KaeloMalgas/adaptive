import random
import json

def generate_questions():
    questions = [
        {
            "question": "What is the capital of France?",
            "options": ["Paris", "London", "Berlin", "Madrid"],
            "correct_answer": "Paris"
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Mars", "Venus", "Jupiter", "Saturn"],
            "correct_answer": "Mars"
        },
        {
            "question": "Who painted the Mona Lisa?",
            "options": ["Leonardo da Vinci", "Vincent van Gogh", "Pablo Picasso", "Michelangelo"],
            "correct_answer": "Leonardo da Vinci"
        },
        {
            "question": "What is the largest mammal in the world?",
            "options": ["Blue Whale", "African Elephant", "Giraffe", "Hippopotamus"],
            "correct_answer": "Blue Whale"
        },
        {
            "question": "Which element has the chemical symbol 'O'?",
            "options": ["Oxygen", "Gold", "Silver", "Iron"],
            "correct_answer": "Oxygen"
        },
        {
            "question": "In which year did World War II end?",
            "options": ["1945", "1939", "1941", "1950"],
            "correct_answer": "1945"
        },
        {
            "question": "What is the largest organ in the human body?",
            "options": ["Skin", "Liver", "Heart", "Brain"],
            "correct_answer": "Skin"
        },
        {
            "question": "Which country is home to the kangaroo?",
            "options": ["Australia", "New Zealand", "South Africa", "Brazil"],
            "correct_answer": "Australia"
        },
        {
            "question": "What is the square root of 64?",
            "options": ["8", "6", "10", "12"],
            "correct_answer": "8"
        },
        {
            "question": "Who wrote the play 'Romeo and Juliet'?",
            "options": ["William Shakespeare", "Charles Dickens", "Jane Austen", "Mark Twain"],
            "correct_answer": "William Shakespeare"
        }
    ]

    # Shuffle the options for each question
    for q in questions:
        correct_answer = q["correct_answer"]
        options = q["options"]
        random.shuffle(options)
        q["correct_index"] = options.index(correct_answer)

    return questions

if __name__ == "__main__":
    questions = generate_questions()
    
    # Save questions to a JSON file
    with open('data/questions.json', 'w') as f:
        json.dump(questions, f, indent=2)
    
    print("Questions have been generated and saved to data/questions.json")
    
    # Print the questions (for verification)
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}: {q['question']}")
        for j, option in enumerate(q['options']):
            print(f"  {chr(97 + j)}) {option}")
        print(f"Correct answer: {chr(97 + q['correct_index'])}")