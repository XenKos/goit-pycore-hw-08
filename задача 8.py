import re
import pickle
from collections import UserDict
from datetime import datetime, timedelta

def parse_input(user_input):
    parts = user_input.split(maxsplit=1)
    cmd = parts[0].strip().lower()
    args = parts[1].strip() if len(parts) > 1 else None
    return cmd, args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self.value = date_obj

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))
 
    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                break

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def add_birthday(self, date_obj):
        self.birthday = date_obj

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)}"

class AddressBook(UserDict):
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record
        
    def find(self, name):
        for record in self.data.values():
            if record.name.value == name:
                return record
        return None

    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    def get_upcoming_birthdays(self):
        today = datetime.now()
        next_week = today + timedelta(days=7)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                if today <= next_birthday <= next_week:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays
    
    def save_data(book, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(book, f)
        
    def load_data(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = AddressBook()
    book.load_data() 
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)  
         
        if command in ['exit', 'close']:
            print("Good bye!")
            break

        elif command == 'hello':
            print("How can I help you?")

        elif command == 'add':
            try:
                name, *phones = args.split()
                record = Record(name)
                for phone in phones:
                    if not re.match(r'^\d{10}$', phone):
                        raise ValueError("Invalid phone number format")
                    record.add_phone(phone)
                book.add_record(record)
                print("Contact added.")
            except ValueError as e:
                print(e)

        elif command == 'change':
            name, new_phone = args.split()
            record = book.find(name)
            if record:
                try:
                    record.edit_phone(record.phones[0].value, new_phone)
                    print("Contact updated.")
                except ValueError as e:
                    print(e)
            else:
                print("Contact not found.")

        elif command == 'phone':
            name = args.strip()
            record = book.find(name)
            if record:
                print(f"\n{name}'s phone number: {record.phones[0].value}")
            else:
                print("Contact not found.")

        elif command == 'find':
            name = args.strip()
            record = book.find(name)
            if record:
                 print(f"Found record: {record}")
            else:
                 print("Record not found.")

        elif command == 'delete':
            name = args.strip()
            if name in book.data:
                book.delete(name)
                print(f"Record '{name}' deleted successfully.")
            else:
                print("Record not found.")
                 
        elif command == 'all':
            if book:
                result = "All contacts:"
                for name, record in book.data.items():
                    result += f"\n{name}: {record.phones[0].value}"
                print(result)
            else:
                print("Phonebook is empty.")
      
        elif command == "add-birthday":
            if args:
                name, birthday_str = args.split()
                try:
                    record = book.find(name)
                    if record:
                        birthday = datetime.strptime(birthday_str, "%d.%m.%Y")
                        record.add_birthday(birthday)
                        print("Birthday's date added")
                    else:
                        print("Contact not found")
                except ValueError as e:
                    print(e)
            else:
                print("Invalid command format. Please provide name and birthday.")

        elif command == "show-birthday":
            name = args.strip()
            record = book.find(name)
            if record:
                if record.birthday:
                    print(f"{name}'s Birthday is: {record.birthday.strftime('%d.%m.%Y')}")
                else:
                    print(f"{name} has no registered birthday.")
            else:
                print("Contact not found.")

        elif command == "birthdays":
            upcoming_birthdays = book.get_upcoming_birthdays()
            if upcoming_birthdays:
                print("Users to greet in the next week:")
                for record in upcoming_birthdays:
                    print(record.name)
            else:
                print("No upcoming birthdays in the next week.")

        else:
            print("Invalid command. Please try again.")
    
if __name__ == "__main__":
    book = AddressBook()
    book.load_data()  # Завантаження даних перед початком роботи програми
    main()
    book.save_data()