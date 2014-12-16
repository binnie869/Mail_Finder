/* Set Home Directory - where we install software */
%default HOME `echo \$HOME/Software/`

/* Load Avro jars and define shortcut */
REGISTER /usr/lib/pig/pig-0.13.0/lib/avro-1.7.5.jar
REGISTER /usr/lib/pig/pig-0.13.0/lib/json-simple-1.1.jar
REGISTER /usr/lib/pig/pig-0.13.0/contrib/piggybank/java/piggybank.jar
define AvroStorage org.apache.pig.piggybank.storage.avro.AvroStorage();

/* MongoDB libraries and configuration */
REGISTER ../ch03/mongo-hadoop/mongo-2.10.1.jar
REGISTER ../ch03/mongo-hadoop/mongo-hadoop-1.1-1.2.0/mongo-hadoop-core_1.1.2-1.2.0.jar
REGISTER ../ch03/mongo-hadoop/mongo-hadoop-1.1-1.2.0/mongo-hadoop-pig_1.1.2-1.2.0.jar

set mapred.map.tasks.speculative.execution false
set mapred.reduce.tasks.speculative.execution false

/* Set speculative execution off so we don't have the chance of duplicate records in Mongo */
set mapred.map.tasks.speculative.execution false
set mapred.reduce.tasks.speculative.execution false
define MongoStorage com.mongodb.hadoop.pig.MongoStorage(); /* Shortcut */

avros = load '/home/anubhav/courses/298/Agile_Data_Code/ch03/gmail/scrapedInbox' using AvroStorage(); /* For example, 'enron.avro' */
store avros into 'mongodb://localhost:27017/agile_data.full_inbox' using MongoStorage(); /* For example, 'mongodb://localhost/enron.emails' */
