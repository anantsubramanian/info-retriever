info-retriever
==============
A simple information retriever that builds an in-memory index of Documents present in a specified folder and retrieves documents based on queries supplied by the user.

The retriever uses tf-idf (normalized using max frequency of a term in a document) to rank the results. The index can also be saved to disk for static databases.

Options are set in config.cfg

