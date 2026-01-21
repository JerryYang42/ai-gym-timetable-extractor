"""
Example usage of the GymScheduleExtractor.

This script demonstrates how to:
1. Extract gym schedule from images
2. Store classes in the in-memory database
3. Query the database for classes
4. Handle duplicate uploads
"""

from GymScheduleExtractor import GymScheduleExtractor, GymClass, GymSchedule


def example_extract_from_images():
    """Example: Extract schedule from multiple images and store in database."""
    print("=" * 60)
    print("Example 1: Extract from images and store in database")
    print("=" * 60)
    
    extractor = GymScheduleExtractor()
    
    # List of image files to process
    image_files = [
        "data/IMG_7195.PNG",
        "data/IMG_7196.PNG",
        "data/IMG_7197.PNG"
    ]
    
    for image_path in image_files:
        try:
            print(f"\nProcessing: {image_path}")
            result = extractor.extract_and_store(image_path)
            
            print(f"  Extracted {result['total_classes']} classes")
            print(f"  Added: {result['stats']['added']}, Updated: {result['stats']['updated']}")
            
            # Save to output file
            output_path = image_path.replace("data/", "output/").replace(".PNG", ".json")
            extractor.save_to_file(result["schedule"], output_path)
            
        except FileNotFoundError:
            print(f"  ⚠ File not found: {image_path}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Show total classes in database
    all_classes = extractor.database.get_all()
    print(f"\n📊 Total classes in database: {len(all_classes)}")


def example_query_database():
    """Example: Query the database for specific classes."""
    print("\n" + "=" * 60)
    print("Example 2: Query database")
    print("=" * 60)
    
    extractor = GymScheduleExtractor()
    
    # Simulate adding some classes
    sample_classes = [
        GymClass(
            date="2024-01-15",
            day_of_week="Monday",
            timeslot="10:00-11:00",
            activity="Yoga",
            venue="Studio A",
            class_type="Group",
            vacancy=5
        ),
        GymClass(
            date="2024-01-15",
            day_of_week="Monday",
            timeslot="14:00-15:00",
            activity="Pilates",
            venue="Studio B",
            class_type="Group",
            vacancy=3
        ),
        GymClass(
            date="2024-01-16",
            day_of_week="Tuesday",
            timeslot="10:00-11:00",
            activity="Spinning",
            venue="Cycling Studio",
            class_type="Group",
            vacancy=8
        )
    ]
    
    # Add classes to database
    stats = extractor.database.add_or_update_batch(sample_classes)
    print(f"Added {stats['added']} classes, updated {stats['updated']} classes")
    
    # Query all classes
    all_classes = extractor.database.get_all()
    print(f"\n📋 All classes ({len(all_classes)}):")
    for cls in all_classes:
        print(f"  - {cls.activity} on {cls.date} at {cls.timeslot} ({cls.vacancy} spots)")
    
    # Query by date
    print(f"\n📅 Classes on 2024-01-15:")
    classes_on_date = extractor.database.get_by_date("2024-01-15")
    for cls in classes_on_date:
        print(f"  - {cls.activity} at {cls.timeslot} ({cls.vacancy} spots)")


def example_duplicate_handling():
    """Example: Demonstrate duplicate handling with vacancy updates."""
    print("\n" + "=" * 60)
    print("Example 3: Duplicate handling")
    print("=" * 60)
    
    extractor = GymScheduleExtractor()
    
    # Add initial class
    yoga_class_v1 = GymClass(
        date="2024-01-15",
        day_of_week="Monday",
        timeslot="10:00-11:00",
        activity="Yoga",
        venue="Studio A",
        class_type="Group",
        vacancy=5
    )
    
    is_update = extractor.database.add_or_update(yoga_class_v1)
    print(f"First upload - is_update: {is_update}, vacancy: {yoga_class_v1.vacancy}")
    
    # Upload same class with updated vacancy
    yoga_class_v2 = GymClass(
        date="2024-01-15",
        day_of_week="Monday",
        timeslot="10:00-11:00",
        activity="Yoga",
        venue="Studio A",
        class_type="Group",
        vacancy=2  # Updated vacancy
    )
    
    is_update = extractor.database.add_or_update(yoga_class_v2)
    print(f"Second upload - is_update: {is_update}, vacancy: {yoga_class_v2.vacancy}")
    
    # Verify only one class exists
    all_classes = extractor.database.get_all()
    print(f"\n✅ Database correctly contains {len(all_classes)} class(es)")
    print(f"   Vacancy correctly updated to: {all_classes[0].vacancy}")


if __name__ == "__main__":
    print("\n🏋️ Gym Schedule Extractor - Usage Examples\n")
    
    # Example 1: Extract from images (requires API key and image files)
    # Uncomment to run:
    # example_extract_from_images()
    
    # Example 2: Query database
    example_query_database()
    
    # Example 3: Duplicate handling
    example_duplicate_handling()
    
    print("\n✨ Examples completed!\n")
