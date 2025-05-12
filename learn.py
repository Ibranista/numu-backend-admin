class Person:
    MALE = 'male'
    FEMALE = 'female'
    email = "myemail@gmail"

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        print(f"Hello, my name is {self.name} and I am {self.age} years old.")

    def __str__(self):
        return self.name

class Student(Person):
    def __init__(self, name, age,gender,email):
        super().__init__(name, age)
        self.gender = gender
        self.email = email
    
    def __str__(self):
        return f"Hello, my name is {self.name}, I am {self.gender} and I am {self.age} years having email of {self.email}."

student1 = Student("Girum", 20,Student.FEMALE,Student.email)
print(student1.MALE)  # Output: Hello, my name is Alice and I am 20 years old.

# print("# --------understanding------------")

names = ["Alice", "Bob", "Charlie"];

def get_or_create(name):
    if name in names:
        created = False
    else:
        names.append(name)
        created = True
    return name, created

result, created = get_or_create("Alice")
print(result)  # Output: Alice
print(created)  # Output: False
