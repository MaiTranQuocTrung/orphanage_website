"""Sample content for the shelter website."""

EVENTS = [
    {
        "id": 1,
        "title": "Spring Festival Celebration",
        "date": "March 15, 2026",
        "summary": "A joyful day of music, games, and community gathering for children and families.",
        "image": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=800&q=80",
        "link": "#",
    },
    {
        "id": 2,
        "title": "Annual Charity Run",
        "date": "April 22, 2026",
        "summary": "Join us for a 5K run to raise funds for education and healthcare programs.",
        "image": "https://images.unsplash.com/photo-1452626212852-811ad9903749?w=800&q=80",
        "link": "#",
    },
    {
        "id": 3,
        "title": "Volunteer Appreciation Day",
        "date": "May 10, 2026",
        "summary": "Honoring the dedicated volunteers who make our mission possible every day.",
        "image": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&q=80",
        "link": "#",
    },
]

STORIES = [
    {
        "id": 1,
        "title": "Minh's Journey to Hope",
        "date": "February 2026",
        "excerpt": "After years of uncertainty, Minh found a loving home and discovered his passion for art.",
        "image": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800&q=80",
        "link": "#",
    },
    {
        "id": 2,
        "title": "A Community That Cares",
        "date": "January 2026",
        "excerpt": "Local businesses and neighbors came together to renovate our learning center.",
        "image": "https://images.unsplash.com/photo-1488521787591-d7eba9b9a1fe?w=800&q=80",
        "link": "#",
    },
    {
        "id": 3,
        "title": "Lan Finds Her Voice",
        "date": "December 2025",
        "excerpt": "Through music therapy and mentorship, Lan gained confidence to perform at our annual concert.",
        "image": "https://images.unsplash.com/photo-1503676260728-1c00da280a25?w=800&q=80",
        "link": "#",
    },
]

FOUNDING_COUNCIL = [
    {
        "id": "council-1",
        "name": "Dr. Nguyễn Thị Hoa",
        "role": "Chairperson",
        "photo": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80",
        "bio": "Dr. Hoa has dedicated over 25 years to child welfare advocacy. She founded Tuệ Quang Children with a vision of providing every child a safe, nurturing environment.",
    },
    {
        "id": "council-2",
        "name": "Rev. Trần Văn Bình",
        "role": "Vice Chairperson",
        "photo": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&q=80",
        "bio": "Rev. Bình brings spiritual guidance and community outreach expertise. He has served vulnerable families across the region for two decades.",
    },
    {
        "id": "council-3",
        "name": "Ms. Lê Thị Mai",
        "role": "Secretary",
        "photo": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&q=80",
        "bio": "Ms. Mai oversees administrative operations and legal compliance. Her background in nonprofit management ensures transparent governance.",
    },
    {
        "id": "council-4",
        "name": "Mr. Phạm Đức Anh",
        "role": "Treasurer",
        "photo": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&q=80",
        "bio": "Mr. Anh manages financial stewardship with integrity. A certified accountant, he ensures every donation reaches those who need it most.",
    },
]

ORG_CHART = [
    {
        "level": 1,
        "title": "Executive Director",
        "members": [
            {
                "name": "Dr. Nguyễn Thị Hoa",
                "role": "Executive Director",
                "photo": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&q=80",
                "bio": "Provides overall leadership and strategic direction for the shelter.",
            }
        ],
    },
    {
        "level": 2,
        "title": "Department Heads",
        "members": [
            {
                "name": "Ms. Trần Thị Lan",
                "role": "Director of Care",
                "photo": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=200&q=80",
                "bio": "Oversees daily care, counseling, and wellbeing of all children.",
            },
            {
                "name": "Mr. Hoàng Văn Tú",
                "role": "Director of Education",
                "photo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80",
                "bio": "Manages educational programs, tutoring, and school partnerships.",
            },
            {
                "name": "Ms. Võ Thị Hương",
                "role": "Director of Operations",
                "photo": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&q=80",
                "bio": "Handles facilities, logistics, and volunteer coordination.",
            },
        ],
    },
    {
        "level": 3,
        "title": "Care Team",
        "members": [
            {
                "name": "Ms. Đặng Thị Ngọc",
                "role": "Senior Caregiver",
                "photo": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&q=80",
                "bio": "Leads the residential care team and mentors new staff.",
            },
            {
                "name": "Mr. Bùi Minh Khang",
                "role": "Youth Counselor",
                "photo": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&q=80",
                "bio": "Provides emotional support and life skills coaching for teens.",
            },
            {
                "name": "Ms. Phan Thị Thu",
                "role": "Health Coordinator",
                "photo": "https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=200&q=80",
                "bio": "Coordinates medical checkups, nutrition, and wellness programs.",
            },
            {
                "name": "Mr. Lý Quốc Huy",
                "role": "Education Specialist",
                "photo": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&q=80",
                "bio": "Designs curriculum and supports children with learning needs.",
            },
        ],
    },
]


def get_recent_events(limit=3):
    return EVENTS[:limit]


def get_recent_stories(limit=3):
    return STORIES[:limit]
