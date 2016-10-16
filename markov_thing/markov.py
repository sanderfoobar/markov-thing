import sys
import json
import argparse
import sqlite3
import codecs
import os
from markov_thing.db import Db
from markov_thing.gen import Generator
from markov_thing.parse import Parser
from markov_thing.sql import Sql
from markov_thing.rnd import Rnd


class MarkovText:
    def __init__(self):
        self.cwd = self._cwd()

        self._sentence_separator = '.'
        self._word_separator = ' '

    def list_databases(self):
        dbs = []
        for f in os.listdir(self.cwd):
            if f.endswith(".sqlite3"):
                dbs.append(f.replace(".sqlite3", ""))

        return dbs

    def parse(self, input_file, depth):
        file_data = self._input_file(input_file)

        if os.path.exists(file_data["output_file"]):
            os.remove(file_data["output_file"])

        db = Db(sqlite3.connect(file_data["output_file"]), Sql())
        db.setup(depth)

        corpus = codecs.open(file_data["input_file"], 'r', 'utf-8').read()
        Parser(file_data["name"], db, self._sentence_separator, self._word_separator).parse(corpus)

    def generate(self, database, minc=0, maxc=256):
        file_data = self._input_file(database)

        db = Db(sqlite3.connect(file_data["output_file"]), Sql())

        generator = Generator(file_data["name"], db, Rnd())
        generated = generator.generate(self._word_separator)

        while len(generated) > maxc or len(generated) < minc:
            generated = generator.generate(self._word_separator)

        return generated

    def _cwd(self):
        cwd = "%s/.markov-thing/" % os.path.expanduser("~")
        if not os.path.exists(cwd):
            os.mkdir(cwd)

        return cwd

    def _input_file(self, input_file):
        name = os.path.basename(input_file)
        if "." in name:
            name = "".join(name.split(".", 1)[0])
        name = name
        output_file = "%s%s.sqlite3" % (self.cwd, name)

        return {
            "name": name,
            "input_file": input_file,
            "output_file": output_file
        }


def json_err(msg):
    return {"error": msg}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", help="mode", action="store")
    parser.add_argument("-d", "--depth", type=int, help="A numeric value (minimum 2) which determines how many of the previous words are used to select the next word. Normally a depth of 2 is used, meaning that each word is selected based only on the previous one. The larger the depth value, the more similar the generated sentences will be to those appearing in the source text. Beyond a certain depth the generated sentences will be identical to those appearing in the source.", default=2, action="store")
    parser.add_argument("-i", "--input-file", help="The (full) location of the source text file when running in mode \"parse\".", action="store")
    parser.add_argument("-db", "--database", help="The name of the database", action="store")
    parser.add_argument("-minc", "--min-characters", type=int, default=0, help="The minimum amount of characters to generate", action="store")
    parser.add_argument("-maxc", "--max-characters", type=int, default=256, help="The maximum amount of characters to generate", action="store")
    parser.add_argument("-dbs", "--list-databases", help="List the available databases", action="store_true")
    args = parser.parse_args()

    if args.list_databases:
        markov = MarkovText()
        databases = markov.list_databases()
        sys.stdout.write(json.dumps({"databases": databases}))
        sys.exit()

    if args.mode == "gen":
        database = args.database
        if not database:
            json_err("db not specified")
            sys.exit(1)

        min_characters = args.min_characters
        max_characters = args.max_characters

        markov = MarkovText()
        generated = markov.generate(database=database,
                                    minc=min_characters,
                                    maxc=max_characters)

        sys.stdout.write(json.dumps({"generated": generated}))
        sys.exit()

    if args.mode == "parse":
        input_file = args.input_file
        if not input_file:
            json_err("file not found")
            sys.exit(1)

        depth = args.depth

        markov = MarkovText()
        markov.parse(input_file=input_file, depth=depth)
        sys.exit(0)

    parser.print_help()

if __name__ == "__main__":
    main()