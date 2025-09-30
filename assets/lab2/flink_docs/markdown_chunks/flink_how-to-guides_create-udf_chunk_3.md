---
document_id: flink_how-to-guides_create-udf_chunk_3
source_file: flink_how-to-guides_create-udf.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/create-udf.html
title: Create a User-Defined Function with Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 7
---

"XS"),
                           new Size("Small", "S"),
                           new Size("Medium", "M"),
                           new Size("Large", "L"),
                           new Size("X-Large", "XL"),
                           new Size("XX-Large", "XXL"));

            public boolean eval(String shirt1, String shirt2) {
               int size1 = findSize(shirt1);
               int size2 = findSize(shirt2);
               // If either can't be found just say false rather than throw an error
               if (size1 == -1 || size2 == -1) {
                     return false;
               }
               return size1 < size2;
            }

            private int findSize(String shirt) {
               return IntStream.range(0, ORDERED_SIZES.size())
                        .filter(
                                 i -> {
                                    Size s = ORDERED_SIZES.get(i);
                                    return s.name.equalsIgnoreCase(shirt)
                                             || s.abbreviation.equalsIgnoreCase(shirt);
                                 })
                        .findFirst()
                        .orElse(-1);
            }

            private static class Size {
               private final String name;
               private final String abbreviation;

               public Size(String name, String abbreviation) {
                     this.name = name;
                     this.abbreviation = abbreviation;
               }
            }
         }

  5. Run the following command to build the jar file.

         mvn clean package

  6. Run the following command to check the contents of your jar.

         jar -tf target/udf_example-1.0.jar | grep -i TShirtSizingIsSmaller

Your output should resemble:

         com/example/my/TShirtSizingIsSmaller$Size.class
         com/example/my/TShirtSizingIsSmaller.class
