# Source Requirements — Smart Learning Through Tunes & Cartoons

This document records the requirements used while completing the implementation.

## Supplied project objective

Develop an interactive web-based e-learning platform that helps young children learn nursery rhymes through animated videos, synchronized audio, smart repetition and gamified quizzes.

## Core modules from the supplied PPT

1. User Interface Module
2. User Authentication Module
3. Learning Management Module
4. Quiz Module
5. Progress Tracking Module
6. Database / Storage Module

## Proposed workflow

Login / Register → Select rhyme → Play video/audio → Smart Repeat → Take quiz → Submit answers → Display score → Store progress.

## User roles shown by the source diagrams

### Child / Learner
- Register / Login
- View rhymes
- Play cartoon videos
- Listen to audio
- Repeat/loop rhymes
- Take quiz
- View score

### Parent
- Login
- Monitor child progress
- View quiz results

### Admin / Content Manager
- Login
- Add/edit/delete rhymes
- Upload video
- Upload audio
- Manage quizzes
- Manage users

## Current-scope decision

The supplied PPT places AI-based personalized learning and voice recognition under **Future Enhancement**. They are therefore not treated as mandatory current-scope features and no AI API key is required.

## Media note

The supplied ZIP contains no real nursery-rhyme video/audio assets. The implementation therefore supports uploaded media and includes a browser voice fallback so a lesson remains demonstrable without inventing external media.
